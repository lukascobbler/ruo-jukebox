from iac.dynamo_db_stack import DynamoDbStack
from constructs import Construct
from aws_cdk import (
    aws_lambda_event_sources as lambda_events,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    Duration,
    Stack
)


class InteractionsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack,
                 environment, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_interactions_processing(dynamo_db, environment)

    def _init_interactions_processing(self, dynamo_db, env):
        # feed builders from user activity and subscriptions
        interactions_feed_fn = _lambda.Function(
            self, "InteractionsFeed",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_interaction"),
            environment=env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )
        inter_stream_dlq = sqs.Queue(self, "InteractionsStreamDLQ", retention_period=Duration.days(14))
        interactions_feed_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.interactions,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(inter_stream_dlq),
            report_batch_item_failures=True,
        ))
        for t in [dynamo_db.tracks, dynamo_db.albums, dynamo_db.artists, dynamo_db.feed]:
            t.grant_read_write_data(interactions_feed_fn)
