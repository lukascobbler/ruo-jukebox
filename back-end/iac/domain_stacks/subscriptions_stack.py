from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared_layer_stack import SharedLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.auth_layer_stack import AuthLayerStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack
from iac.email_stack import EmailStack
from constructs import Construct
from aws_cdk import (
    aws_apigateway as apigw,
    Stack
)


class SubscriptionsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack, s3: S3Stack, shared_layer_stack: SharedLayerStack, auth_layer_stack: AuthLayerStack, api_stack: ApiGatewayStack, email_stack: EmailStack,
                 environment, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.lambdas = {}
        self._create_lambdas(dynamo_db, s3, shared_layer_stack, auth_layer_stack, environment)
        self._attach_to_api(api_stack)

    def _create_lambdas(self, dynamo_db, s3, shared_layer_stack, auth_layer_stack, env):
        lambda_defs = {
            "SubsCreate": "services/subscriptions/create",
            "SubsListMine": "services/subscriptions/list_mine",
            "SubsDelete": "services/subscriptions/delete"
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, shared_layer_stack, auth_layer_stack).fn

    def _attach_to_api(self, api: ApiGatewayStack):
        subs = api.api.root.add_resource("subscriptions")
        subs.add_method("POST", apigw.LambdaIntegration(self.lambdas["SubsCreate"]), **api.auth_kwargs)

        mine = subs.add_resource("mine")
        mine.add_method("GET", apigw.LambdaIntegration(self.lambdas["SubsListMine"]), **api.auth_kwargs)

        topic = subs.add_resource("{topic}")
        topic.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["SubsDelete"]), **api.auth_kwargs)