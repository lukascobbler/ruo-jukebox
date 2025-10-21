from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared_layer_stack import SharedLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.utils_layer_stack import UtilsLayerStack
from iac.auth_layer_stack import AuthLayerStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.email_stack import EmailStack
from iac.s3_stack import S3Stack
from constructs import Construct
from aws_cdk import (
    aws_lambda_event_sources as lambda_events,
    aws_apigateway as apigw,
    aws_lambda as _lambda, Duration,
    aws_sqs as sqs,
    Stack
)


class SubscriptionsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack, s3: S3Stack, shared_layer_stack: SharedLayerStack, auth_layer_stack: AuthLayerStack,
                 utils_layer_stack: UtilsLayerStack, api_stack: ApiGatewayStack, email_stack: EmailStack, environment, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.lambdas = {}
        self._create_lambdas(dynamo_db, s3, shared_layer_stack, auth_layer_stack, utils_layer_stack, environment)
        self._attach_to_api(api_stack)
        self._init_subscription_processing(dynamo_db, email_stack, environment)

    def _create_lambdas(self, dynamo_db, s3, shared_layer_stack, auth_layer_stack, utils_layer_stack, env):
        lambda_defs = {
            "SubsCreate": "services/subscriptions/create",
            "SubsListMine": "services/subscriptions/list_mine",
            "SubsDelete": "services/subscriptions/delete"
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, shared_layer_stack, auth_layer_stack, utils_layer_stack).fn

    def _attach_to_api(self, api: ApiGatewayStack):
        subs = api.api.root.add_resource("subscriptions")
        subs.add_method("POST", apigw.LambdaIntegration(self.lambdas["SubsCreate"]), **api.auth_kwargs)

        mine = subs.add_resource("mine")
        mine.add_method("GET", apigw.LambdaIntegration(self.lambdas["SubsListMine"]), **api.auth_kwargs)

        topic = subs.add_resource("{topic}")
        topic.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["SubsDelete"]), **api.auth_kwargs)

    def _init_subscription_processing(self, dynamo_db, email_stack, env):
        subs_feed_fn = _lambda.Function(
            self, "SubscriptionsFeed",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_subscription_change"),
            environment=env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )
        for t in [dynamo_db.artists, dynamo_db.albums, dynamo_db.feed]:
            t.grant_read_write_data(subs_feed_fn)

        subs_stream_dlq = sqs.Queue(self, "SubscriptionsStreamDLQ", retention_period=Duration.days(14))
        subs_feed_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.subscriptions,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(subs_stream_dlq),
            report_batch_item_failures=True,
        ))

        release_notify_fn = _lambda.Function(
            self, "ReleaseNotify",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_music_release"),
            environment=env,
            timeout=Duration.seconds(120),
            memory_size=768,
        )

        for t in [
            dynamo_db.artists,
            dynamo_db.albums,
            dynamo_db.songs,
            dynamo_db.content_genres,
            dynamo_db.song_artists,
            dynamo_db.subscriptions,
            dynamo_db.users,
            dynamo_db.feed,
        ]:
            t.grant_read_write_data(release_notify_fn)

        release_notify_fn.role.add_managed_policy(email_stack.send_policy)

        albums_dlq = sqs.Queue(self, "AlbumsStreamDLQ", retention_period=Duration.days(14))
        songs_dlq = sqs.Queue(self, "SongsStreamDLQ", retention_period=Duration.days(14))

        release_notify_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.albums,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(albums_dlq),
            report_batch_item_failures=True,
        ))
        release_notify_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.songs,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(songs_dlq),
            report_batch_item_failures=True,
        ))
