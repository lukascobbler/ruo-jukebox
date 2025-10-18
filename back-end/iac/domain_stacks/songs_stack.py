from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared_layer_stack import SharedLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.cognito_stack import CognitoStack
from iac.s3_stack import S3Stack
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_events,
    Duration,
    aws_sqs as sqs,
    aws_iam as iam
)


class SongsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 cognito: CognitoStack, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack, shared_layer_stack: SharedLayerStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_endpoints(dynamo_db, s3, api_gateway, shared_layer_stack, env)
        self._init_song_processing(cognito, dynamo_db, s3, env)
        self._init_rating_processing(dynamo_db, env)

    def _init_endpoints(self, dynamo_db, s3, api_gateway, shared_layer_stack, env):
        song_init = LambdaWithPermissions(self, "SongInitUpload", "services/songs/init_upload", env, dynamo_db, s3, shared_layer_stack).fn
        song_done = LambdaWithPermissions(self, "SongCompleteUpload", "services/songs/complete_upload", env, dynamo_db, s3, shared_layer_stack).fn
        song_list = LambdaWithPermissions(self, "SongList", "services/songs/list", env, dynamo_db, s3, shared_layer_stack).fn
        song_get = LambdaWithPermissions(self, "SongGet", "services/songs/get", env, dynamo_db, s3, shared_layer_stack).fn
        song_update = LambdaWithPermissions(self, "SongUpdate", "services/songs/update", env, dynamo_db, s3, shared_layer_stack).fn
        song_delete = LambdaWithPermissions(self, "SongDelete", "services/songs/delete", env, dynamo_db, s3, shared_layer_stack).fn
        song_cov_init = LambdaWithPermissions(self, "SongCoverInit", "services/songs/init_cover_upload", env, dynamo_db, s3, shared_layer_stack).fn
        song_cov_done = LambdaWithPermissions(self, "SongCoverDone", "services/songs/complete_cover", env, dynamo_db, s3, shared_layer_stack).fn

        ratings_put = LambdaWithPermissions(self, "SongRatingPut", "services/song-ratings/put", env, dynamo_db, s3, shared_layer_stack).fn
        ratings_delete = LambdaWithPermissions(self, "SongRatingDelete", "services/song-ratings/delete", env, dynamo_db, s3, shared_layer_stack).fn

        song = api_gateway.api.root.add_resource("song")
        song_id = song.add_resource("{id}")
        rating = song_id.add_resource("rating")

        song.add_resource("init-upload").add_method(
            "POST",
            apigw.LambdaIntegration(song_init),
            **api_gateway.auth_kwargs
        )
        song.add_resource("complete-upload").add_method(
            "POST",
            apigw.LambdaIntegration(song_done),
            **api_gateway.auth_kwargs
        )
        song.add_method(
            "GET",
            apigw.LambdaIntegration(song_list),
            **api_gateway.auth_kwargs
        )
        song.add_resource("init-cover-upload").add_method(
            "POST",
            apigw.LambdaIntegration(song_cov_init),
            **api_gateway.auth_kwargs
        )
        song.add_resource("complete-cover").add_method(
            "POST",
            apigw.LambdaIntegration(song_cov_done),
            **api_gateway.auth_kwargs
        )

        song_id.add_method(
            "GET",
            apigw.LambdaIntegration(song_get),
            **api_gateway.auth_kwargs
        )
        song_id.add_method(
            "PATCH",
            apigw.LambdaIntegration(song_update),
            **api_gateway.auth_kwargs
        )
        song_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(song_delete),
            **api_gateway.auth_kwargs
        )

        rating.add_method(
            "PUT",
            apigw.LambdaIntegration(ratings_put),
            **api_gateway.auth_kwargs
        )
        rating.add_method(
            "DELETE",
            apigw.LambdaIntegration(ratings_delete),
            **api_gateway.auth_kwargs
        )

    def _init_song_processing(self, cognito, dynamo_db, s3, env):
        # 1 New content (Albums + Tracks) -> notify subscribers, add feed cards, start transcription for tracks
        song_events_fn = _lambda.Function(
            self, "ContentEvents",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_content_change"),
            environment=env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )

        for t in [dynamo_db.albums, dynamo_db.tracks, dynamo_db.artists, dynamo_db.users, dynamo_db.content_genres,
                  dynamo_db.subscriptions, dynamo_db.feed, dynamo_db.transcriptions]:
            t.grant_read_write_data(song_events_fn)
        s3.audio_bucket.grant_read(song_events_fn)  # if you kick off Transcribe on S3 media
        s3.images_bucket.grant_read(song_events_fn)
        s3.transcripts_bucket.grant_read_write(song_events_fn)

        # SES + Cognito lookup + start transcription
        song_events_fn.add_to_role_policy(
            iam.PolicyStatement(actions=["ses:SendEmail", "ses:SendRawEmail"], resources=["*"]))
        song_events_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["cognito-idp:AdminGetUser"],
            resources=[f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{cognito.user_pool.user_pool_id}"]
        ))
        song_events_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["transcribe:StartTranscriptionJob"], resources=["*"]
        ))

        # DLQs for each stream mapping
        albums_stream_dlq = sqs.Queue(self, "AlbumsStreamDLQ", retention_period=Duration.days(14))
        tracks_stream_dlq = sqs.Queue(self, "TracksStreamDLQ", retention_period=Duration.days(14))

        song_events_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.albums,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,  # if error, split batch and try again
            on_failure=lambda_events.SqsDlq(albums_stream_dlq),  # where to send failed items (dead letter queue)
            report_batch_item_failures=True,  # if some fail, return the failures and aws tries again
        ))
        song_events_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.tracks,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(tracks_stream_dlq),
            report_batch_item_failures=True,
        ))

    def _init_rating_processing(self, dynamo_db, env):
        # Ratings aggregator (Ratings stream NEW_AND_OLD_IMAGES -> update target entities)
        ratings_agg_fn = _lambda.Function(
            self, "RatingsAggregator",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_ratings_change"),
            environment=env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )
        ratings_stream_dlq = sqs.Queue(self, "RatingsStreamDLQ", retention_period=Duration.days(14))
        ratings_agg_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.ratings,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(ratings_stream_dlq),
            report_batch_item_failures=True,
        ))

        # entity tables updated by aggregator
        dynamo_db.tracks.grant_read_write_data(ratings_agg_fn)
        dynamo_db.albums.grant_read_write_data(ratings_agg_fn)
        dynamo_db.artists.grant_read_write_data(ratings_agg_fn)
        dynamo_db.playlists.grant_read_write_data(ratings_agg_fn)
