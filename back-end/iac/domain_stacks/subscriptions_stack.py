from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared_layer_stack import SharedLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda, Duration,
    aws_lambda_event_sources as lambda_events,
    aws_sqs as sqs,
)


class SubscriptionsStack(Stack):
    def __init__(self, scope: Construct, id: str, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack, shared_layer_stack: SharedLayerStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_endpoints(dynamo_db, s3, api_gateway, shared_layer_stack, env)
        self._init_subscription_processing(dynamo_db, env)

    def _init_endpoints(self, dynamo_db, s3, api_gateway, shared_layer_stack, env):
        subs_create = LambdaWithPermissions(self, "SubsCreate", "services/subscriptions/create", env, dynamo_db, s3, shared_layer_stack).fn
        subs_list = LambdaWithPermissions(self, "SubsListMine", "services/subscriptions/list_mine", env, dynamo_db, s3, shared_layer_stack).fn
        subs_delete = LambdaWithPermissions(self, "SubsDelete", "services/subscriptions/delete", env, dynamo_db, s3, shared_layer_stack).fn

        # todo zavrsiti endpointove za subskripcije

    def _init_subscription_processing(self, dynamo_db, env):
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
