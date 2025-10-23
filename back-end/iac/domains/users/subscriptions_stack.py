from iac.custom_constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk import NestedStack, aws_apigateway as apigw
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
    aws_lambda_event_sources as events,
    aws_iam as iam,
)

class SubscriptionsStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str,
                 dynamo_db: DynamoDbStack, s3: S3Stack, libs_layer_stack: LibsLayerStack, auth_layer_stack: AuthLayerStack,
                 utils_layer_stack: UtilsLayerStack, api_stack: ApiGatewayStack, environment, branch, **kwargs):
        super().__init__(scope, stack_id, **kwargs)
        self.lambdas = {}

        # sqs setup

        # singles and albums sends messages here
        self.new_content_dlq = sqs.Queue(
            self, "NewContentDLQ",
            retention_period=Duration.days(14),
        )
        self.new_content_queue = sqs.Queue(
            self, "NewContentQueue",
            visibility_timeout=Duration.seconds(60),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=5, queue=self.new_content_dlq
            ),
        )

        # just sends emails
        self.email_send_dlq = sqs.Queue(
            self, "EmailSendDLQ",
            retention_period=Duration.days(14),
        )
        self.email_send_queue = sqs.Queue(
            self, "EmailSendQueue",
            visibility_timeout=Duration.seconds(60),
            dead_letter_queue=sqs.DeadLetterQueue(max_receive_count=5, queue=self.email_send_dlq),
        )

        self._create_lambdas(dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, environment, branch)
        self._attach_to_api(api_stack)

        # setup workers for sqs

        # aggregator
        notify_fn = self.lambdas["SubsNotifyNewContent"]
        notify_fn.add_event_source(events.SqsEventSource(self.new_content_queue, batch_size=10))
        notify_fn.add_environment("EMAIL_SEND_QUEUE_URL", self.email_send_queue.queue_url)
        self.email_send_queue.grant_send_messages(notify_fn)

        # email sender
        sender_fn = self.lambdas["SubsSendEmail"]
        sender_fn.add_event_source(events.SqsEventSource(self.email_send_queue, batch_size=10))

        sender_fn.role.add_to_principal_policy(iam.PolicyStatement(
            actions=["ses:SendEmail", "ses:SendRawEmail"],
            resources=["*"]
        ))
        sender_fn.add_environment("FROM_EMAIL", environment["FROM_EMAIL"])

    def _create_lambdas(self, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, env, branch):
        lambda_defs = {
            "SubsCreate": "services/subscriptions/create",
            "SubsListMine": "services/subscriptions/list_mine",
            "SubsDelete": "services/subscriptions/delete",
            "SubsNotifyNewContent": "services/subscriptions/notify_new_content",
            "SubsSendEmail": "services/subscriptions/send_email",      
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, branch).fn

    def _attach_to_api(self, api: ApiGatewayStack):
        subs = api.api.root.add_resource("subscriptions")
        subs.add_method("POST", apigw.LambdaIntegration(self.lambdas["SubsCreate"]), **api.auth_kwargs)

        mine = subs.add_resource("mine")
        mine.add_method("GET", apigw.LambdaIntegration(self.lambdas["SubsListMine"]), **api.auth_kwargs)

        topic = subs.add_resource("{topic}")
        topic.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["SubsDelete"]), **api.auth_kwargs)
