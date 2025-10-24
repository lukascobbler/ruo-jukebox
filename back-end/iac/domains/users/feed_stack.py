from iac.custom_constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared.api_gateway_stack import ApiGatewayStack
from iac.layers.utils_layer_stack import UtilsLayerStack
from iac.layers.libs_layer_stack import LibsLayerStack
from iac.layers.auth_layer_stack import AuthLayerStack
from iac.shared.dynamo_db_stack import DynamoDbStack
from iac.shared.s3_stack import S3Stack
from constructs import Construct
from aws_cdk import (
    NestedStack, Duration,
    aws_apigateway as apigw,
    aws_sqs as sqs,
    aws_lambda_event_sources as events
)

class FeedStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str,
                 dynamo_db: DynamoDbStack, s3: S3Stack, libs_layer_stack: LibsLayerStack, auth_layer_stack: AuthLayerStack,
                 utils_layer_stack: UtilsLayerStack, api_stack: ApiGatewayStack, environment, branch, **kwargs):
        super().__init__(scope, stack_id, **kwargs)
        self.lambdas = {}

        suffix = f"-{branch}" if branch != "main" else ""

        # sqs setup

        # interactions, singles and albums sends messages here
        self.refresh_feed_dlq = sqs.Queue(
            self, "FeedRefreshDLQ",
            queue_name=f"FeedRefreshDLQ{suffix}",
            retention_period=Duration.days(14),
        )
        self.refresh_feed_queue = sqs.Queue(
            self, "FeedRefreshQueue",
            queue_name=f"FeedRefreshQueue{suffix}",
            visibility_timeout=Duration.seconds(60),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=5, queue=self.refresh_feed_dlq
            )
        )

        self._create_lambdas(dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, environment, branch)
        self._attach_to_api(api_stack)

        # setup workers for sqs
        notify_fn = self.lambdas["FeedNotifyRefresh"]
        notify_fn.add_event_source(events.SqsEventSource(self.refresh_feed_queue, batch_size=10))
        notify_fn.add_environment("FEED_REFRESH_USER_QUEUE", self.refresh_feed_queue.queue_url)

    def _create_lambdas(self, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, env, branch):
        lambda_defs = {
            "FeedNotifyRefresh": "services/feed/notify_refresh_feed",
            "GetFeed": "services/feed/get",
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, branch).fn

    def _attach_to_api(self, api: ApiGatewayStack):
        feed = api.api.root.add_resource("feed")
        feed.add_method("GET", apigw.LambdaIntegration(self.lambdas["GetFeed"]), **api.auth_kwargs)
