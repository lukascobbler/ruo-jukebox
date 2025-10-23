from iac.custom_constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk import NestedStack, aws_apigateway as apigw
from iac.layers.utils_layer_stack import UtilsLayerStack
from iac.shared.api_gateway_stack import ApiGatewayStack
from iac.layers.libs_layer_stack import LibsLayerStack
from iac.layers.auth_layer_stack import AuthLayerStack
from iac.shared.dynamo_db_stack import DynamoDbStack
from iac.shared.s3_stack import S3Stack
from constructs import Construct


class GenresStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str,
                 dynamo_db: DynamoDbStack, s3: S3Stack, libs_layer_stack: LibsLayerStack, auth_layer_stack: AuthLayerStack,
                 utils_layer_stack: UtilsLayerStack, api_stack: ApiGatewayStack, environment, branch, **kwargs):
        super().__init__(scope, stack_id, **kwargs)
        self.lambdas = {}
        self._create_lambdas(dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, environment, branch)
        self._attach_to_api(api_stack)

    def _create_lambdas(self, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, env, branch):
        lambda_defs = {
            "GenresCreate": "services/genres/create",
            "GenresList": "services/genres/list",
            "GenresGet": "services/genres/get",
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, branch).fn

    def _attach_to_api(self, api: ApiGatewayStack):
        genres = api.api.root.add_resource("genres")
        genre_id = genres.add_resource("{id}")

        genres.add_method("POST", apigw.LambdaIntegration(self.lambdas["GenresCreate"]), **api.auth_kwargs)
        genres.add_method("GET", apigw.LambdaIntegration(self.lambdas["GenresList"]), **api.auth_kwargs)

        genre_id.add_method("GET", apigw.LambdaIntegration(self.lambdas["GenresGet"]), **api.auth_kwargs)