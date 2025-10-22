from iac.custom_constructs.lambda_with_permissions import LambdaWithPermissions
from iac.layers.utils_layer_stack import UtilsLayerStack
from iac.shared.api_gateway_stack import ApiGatewayStack
from iac.layers.libs_layer_stack import LibsLayerStack
from iac.layers.auth_layer_stack import AuthLayerStack
from iac.shared.dynamo_db_stack import DynamoDbStack
from iac.shared.cognito_stack import CognitoStack
from aws_cdk.aws_iam import PolicyStatement
from aws_cdk import aws_apigateway as apigw
from iac.shared.s3_stack import S3Stack
from constructs import Construct
from aws_cdk import NestedStack


class AuthStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, cognito_stack: CognitoStack, dynamo_db: DynamoDbStack, s3: S3Stack, libs_layers_stack: LibsLayerStack,
                 auth_layer_stack: AuthLayerStack, utils_layer_stack: UtilsLayerStack, api_stack: ApiGatewayStack, env_vars: dict, **kwargs):
        super().__init__(scope, stack_id, **kwargs)
        self.lambdas = {}
        self.cognito_stack = cognito_stack
        self._create_lambdas(dynamo_db, s3, libs_layers_stack, auth_layer_stack, utils_layer_stack, env_vars)
        self._attach_to_api(api_stack)

    def _create_lambdas(self, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, env_vars):
        lambda_defs = {
            "Register": "services/auth/register",
            "Login": "services/auth/login",
            "Logout": "services/auth/logout"
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env_vars, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack).fn

        # Register lambda needs additional Cognito permissions
        self.lambdas["Register"].add_to_role_policy(
            PolicyStatement(
                actions=[
                    "cognito-idp:AdminCreateUser",
                    "cognito-idp:AdminSetUserPassword",
                    "cognito-idp:AdminAddUserToGroup",
                    "cognito-idp:AdminGetUser",
                    "cognito-idp:ListUsers"
                ],
                resources=[self.cognito_stack.user_pool.user_pool_arn]
            )
        )

    def _attach_to_api(self, api: ApiGatewayStack):
        auth = api.api.root.add_resource("auth")
        auth.add_resource("register").add_method("POST", apigw.LambdaIntegration(self.lambdas["Register"]), authorizer=None)
        auth.add_resource("login").add_method("POST", apigw.LambdaIntegration(self.lambdas["Login"]), authorizer=None)
        auth.add_resource("logout").add_method("POST", apigw.LambdaIntegration(self.lambdas["Logout"]))
