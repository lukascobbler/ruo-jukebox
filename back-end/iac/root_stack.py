from iac.shared.shared_resources_stack import SharedResourcesStack
from iac.domains.domain_group_stack import DomainGroupStack
from iac.api_gateway_stack import ApiGatewayStack
from constructs import Construct
from aws_cdk import Stack


class RootStack(Stack):
    def __init__(self, scope: Construct, stack_id: str, branch: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)

        shared = SharedResourcesStack(self, "SharedResourcesStack", branch)
        api_gateway = ApiGatewayStack(self, "ApiGatewayStack", branch, user_pool=shared.cognito_stack.user_pool)
        DomainGroupStack(self, "DomainGroupStack", shared=shared, api_gateway=api_gateway)
