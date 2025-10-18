from constructs import Construct
from aws_cdk.aws_apigateway import AuthorizationType
from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_events,
    Duration,
    aws_sqs as sqs,
    aws_iam as iam
)

from iac.api_gateway_stack import ApiGatewayStack
from iac.cognito_stack import CognitoStack
from iac.common import mk_lambda
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack

class SongsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 cognito: CognitoStack, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_endpoints(cognito, dynamo_db, s3, api_gateway, env)
        self._init_song_processing(cognito, dynamo_db, s3, env)
        self._init_rating_processing(cognito, dynamo_db, s3, env)

    def _init_endpoints(self, cognito, dynamo_db, s3, api_gateway, env):
        auth_kwargs = cognito.auth_kwargs
        authorizer = cognito.authorizer

        song_init = mk_lambda("SongInitUpload", "services/songs/init_upload", env, dynamo_db, s3)
        song_done = mk_lambda("SongCompleteUpload", "services/songs/complete_upload", env, dynamo_db, s3)
        song_list = mk_lambda("SongList", "services/songs/list", env, dynamo_db, s3)
        song_get = mk_lambda("SongGet", "services/songs/get", env, dynamo_db, s3)
        song_update = mk_lambda("SongUpdate", "services/songs/update", env, dynamo_db, s3)
        song_delete = mk_lambda("SongDelete", "services/songs/delete", env, dynamo_db, s3)
        song_cov_init = mk_lambda("SongCoverInit", "services/songs/init_cover_upload", env, dynamo_db, s3)
        song_cov_done = mk_lambda("SongCoverDone", "services/songs/complete_cover", env, dynamo_db, s3)

        ratings_put = mk_lambda("SongRatingPut", "services/song-ratings/put", env, dynamo_db, s3)
        ratings_delete = mk_lambda("SongRatingDelete", "services/song-ratings/delete", env, dynamo_db, s3)

        song = api_gateway.api.root.add_resource("song")
        song_id = song.add_resource("{id}")
        rating = song_id.add_resource("rating")

        song.add_resource("init-upload").add_method(
            "POST",
            apigw.LambdaIntegration(song_init),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song.add_resource("complete-upload").add_method(
            "POST",
            apigw.LambdaIntegration(song_done),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song.add_method(
            "GET",
            apigw.LambdaIntegration(song_list),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song.add_resource("init-cover-upload").add_method(
            "POST",
            apigw.LambdaIntegration(song_cov_init),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song.add_resource("complete-cover").add_method(
            "POST",
            apigw.LambdaIntegration(song_cov_done),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )

        song_id.add_method(
            "GET",
            apigw.LambdaIntegration(song_get),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song_id.add_method(
            "PATCH",
            apigw.LambdaIntegration(song_update),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        song_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(song_delete),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )

        rating.add_method(
            "PUT",
            apigw.LambdaIntegration(ratings_put),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        rating.add_method(
            "DELETE",
            apigw.LambdaIntegration(ratings_delete),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )

    def _init_song_processing(self, cognito, dynamo_db, s3, env):
        # 1 New content (Albums + Tracks) -> notify subscribers, add feed cards, start transcription for tracks
        song_events_fn = _lambda.Function(
            self, "ContentEvents",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
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

    def _init_rating_processing(self, cognito, dynamo_db, s3, env):
        # Ratings aggregator (Ratings stream NEW_AND_OLD_IMAGES -> update target entities)
        ratings_agg_fn = _lambda.Function(
            self, "RatingsAggregator",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
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