from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda, Duration,
    aws_lambda_event_sources as lambda_events,
    aws_sqs as sqs,
)

from iac.api_gateway_stack import ApiGatewayStack
from iac.cognito_stack import CognitoStack
from iac.common import mk_lambda
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack


class RatingsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 cognito: CognitoStack, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)

        auth_kwargs = cognito.auth_kwargs
        authorizer = cognito.authorizer

        subs_create = mk_lambda("SubsCreate",    "subscriptions/create", env, dynamo_db, s3)
        subs_list   = mk_lambda("SubsListMine",  "subscriptions/list_mine", env, dynamo_db, s3)
        subs_delete = mk_lambda("SubsDelete",    "subscriptions/delete", env, dynamo_db, s3)

    def _init_subscription_processing(self, dynamo_db, env):
        subs_feed_fn = _lambda.Function(
            self, "SubscriptionsFeed",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
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