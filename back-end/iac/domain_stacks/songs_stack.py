from iac.auth_layer_stack import AuthLayerStack
from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared_layer_stack import SharedLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.cognito_stack import CognitoStack
from aws_cdk.aws_dynamodb import Table
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
    def __init__(self, scope: Construct, id: str, cognito: CognitoStack,
                 dynamo_db: DynamoDbStack, s3: S3Stack, shared_layer_stack: SharedLayerStack, auth_layer_stack: AuthLayerStack,
                 environment, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.lambdas = {}
        self._create_lambdas(dynamo_db, s3, shared_layer_stack, auth_layer_stack, environment)
        self._init_song_processing(cognito, dynamo_db, s3, environment)
        self._init_rating_processing(dynamo_db, environment)

    def _create_lambdas(self, dynamo_db, s3, shared_layer_stack, auth_layer_stack, env):
        lambda_defs = {
            "SongInitUpload": "services/songs/init_upload",
            "SongCompleteUpload": "services/songs/complete_upload",
            "SongList": "services/songs/list",
            "SongGet": "services/songs/get",
            "SongUpdate": "services/songs/update",
            "SongDelete": "services/songs/delete",
            "SongRatingPut": "services/song-ratings/put",
            "SongRatingDelete": "services/song-ratings/delete"
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, shared_layer_stack, auth_layer_stack).fn

    def attach_to_api(self, api: ApiGatewayStack):
        song = api.api.root.add_resource("song")
        song_id = song.add_resource("{id}")
        rating = song_id.add_resource("rating")

        song.add_resource("init-upload").add_method("POST", apigw.LambdaIntegration(self.lambdas["SongInitUpload"]), **api.auth_kwargs)
        song.add_resource("complete-upload").add_method("POST", apigw.LambdaIntegration(self.lambdas["SongCompleteUpload"]), **api.auth_kwargs)
        song.add_method("GET", apigw.LambdaIntegration(self.lambdas["SongList"]), **api.auth_kwargs)

        song_id.add_method("GET", apigw.LambdaIntegration(self.lambdas["SongGet"]), **api.auth_kwargs)
        song_id.add_method("PATCH", apigw.LambdaIntegration(self.lambdas["SongUpdate"]), **api.auth_kwargs)
        song_id.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["SongDelete"]), **api.auth_kwargs)

        rating.add_method("PUT", apigw.LambdaIntegration(self.lambdas["SongRatingPut"]), **api.auth_kwargs)
        rating.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["SongRatingDelete"]), **api.auth_kwargs)

    def _init_song_processing(self, cognito, dynamo_db, s3, env):
        # 1 New content (Albums + Tracks) -> notify subscribers, add feed cards, start transcription for tracks
        song_events_role = iam.Role(
            self, "ContentEventsRole",
            role_name="ContentEventsLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        song_events_fn = _lambda.Function(
            self, "ContentEvents",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_content_change"),
            environment=env,
            timeout=Duration.seconds(60),
            memory_size=512,
            role=song_events_role
        )

        for table in (t for t in vars(dynamo_db).values() if isinstance(t, Table)):
            table.grant_read_write_data(song_events_fn)
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
        songs_stream_dlq = sqs.Queue(self, "SongsStreamDLQ", retention_period=Duration.days(14))

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
            dynamo_db.songs,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(songs_stream_dlq),
            report_batch_item_failures=True,
        ))

    def _init_rating_processing(self, dynamo_db, env):
        # Ratings aggregator (Ratings stream NEW_AND_OLD_IMAGES -> update target entities)
        song_events_role = iam.Role(
            self, "RatingsAggregatorRole",
            role_name="RatingsAggregatorLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        ratings_agg_fn = _lambda.Function(
            self, "RatingsAggregator",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_ratings_change"),
            environment=env,
            timeout=Duration.seconds(60),
            memory_size=512,
            role=song_events_role
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
        dynamo_db.songs.grant_read_write_data(ratings_agg_fn)
        dynamo_db.albums.grant_read_write_data(ratings_agg_fn)
        dynamo_db.artists.grant_read_write_data(ratings_agg_fn)
        dynamo_db.playlists.grant_read_write_data(ratings_agg_fn)
