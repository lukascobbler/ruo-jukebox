from iac.shared.shared_resources_stack import SharedResourcesStack
from iac.domains.domain_group_stack import DomainGroupStack
from aws_cdk.aws_s3_notifications import LambdaDestination
from iac.shared.api_gateway_stack import ApiGatewayStack
from aws_cdk import Stack, aws_s3
from constructs import Construct


class RootStack(Stack):
    def __init__(self, scope: Construct, stack_id: str, branch: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)

        shared = SharedResourcesStack(self, "SharedResourcesStack", branch)
        api_gateway = ApiGatewayStack(self, "ApiGatewayStack", branch, user_pool=shared.cognito_stack.user_pool)
        domain_group = DomainGroupStack(self, "DomainGroupStack", shared=shared, api_gateway=api_gateway)

        shared.s3_stack.audio_bucket.add_event_notification(
            LambdaDestination(domain_group.transcription_stack.producer_lambda),
            aws_s3.EventType.OBJECT_CREATED,
            aws_s3.NotificationKeyFilter(prefix="songs/", suffix=".mp3")
        )
