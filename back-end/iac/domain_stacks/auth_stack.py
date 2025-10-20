from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared_layer_stack import SharedLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.auth_layer_stack import AuthLayerStack
from iac.dynamo_db_stack import DynamoDbStack
from aws_cdk.aws_iam import PolicyStatement
from aws_cdk import aws_apigateway as apigw
from iac.cognito_stack import CognitoStack
from constructs import Construct
from iac.s3_stack import S3Stack
from aws_cdk import Stack


class AuthStack(Stack):
    def __init__(self, scope: Construct, id: str, cognito_stack: CognitoStack, dynamo_db: DynamoDbStack,
                 s3: S3Stack, shared_layers_stack: SharedLayerStack, auth_layer_stack: AuthLayerStack, api_stack: ApiGatewayStack, env_vars: dict, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.lambdas = {}
        self.cognito_stack = cognito_stack
        self._create_lambdas(dynamo_db, s3, shared_layers_stack, auth_layer_stack, env_vars)
        self._attach_to_api(api_stack)

    def _create_lambdas(self, dynamo_db, s3, shared_layer_stack, auth_layer_stack, env_vars):
        lambda_defs = {
            "Register": "services/auth/register",
            "Login": "services/auth/login",
            "Logout": "services/auth/logout"
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env_vars, dynamo_db, s3, shared_layer_stack, auth_layer_stack).fn

        # Register lambda needs additional Cognito permissions
        self.lambdas["Register"].add_to_role_policy(
            PolicyStatement(
                actions=[
                    "cognito-idp:AdminCreateUser",
                    "cognito-idp:AdminSetUserPassword",
                    "cognito-idp:AdminAddUserToGroup"
                ],
                resources=[self.cognito_stack.user_pool.user_pool_arn]
            )
        )

    def _attach_to_api(self, api: ApiGatewayStack):
        auth = api.api.root.add_resource("auth")
        auth.add_resource("register").add_method("POST", apigw.LambdaIntegration(self.lambdas["Register"]), authorizer=None)
        auth.add_resource("login").add_method("POST", apigw.LambdaIntegration(self.lambdas["Login"]), authorizer=None)
        auth.add_resource("logout").add_method("POST", apigw.LambdaIntegration(self.lambdas["Logout"]))
