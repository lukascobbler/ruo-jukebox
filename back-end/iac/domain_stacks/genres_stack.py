from iac.auth_layer_stack import AuthLayerStack
from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared_layer_stack import SharedLayerStack
from aws_cdk import Stack, aws_apigateway as apigw
from iac.api_gateway_stack import ApiGatewayStack
from iac.dynamo_db_stack import DynamoDbStack
from constructs import Construct
from iac.s3_stack import S3Stack


class GenresStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack, s3: S3Stack, shared_layer_stack: SharedLayerStack, auth_layer_stack: AuthLayerStack,
                 environment, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.lambdas = {}
        self._create_lambdas(dynamo_db, s3, shared_layer_stack, auth_layer_stack, environment)

    def _create_lambdas(self, dynamo_db, s3, shared_layer_stack, auth_layer_stack, env):
        lambda_defs = {
            "GenresCreate": "services/genres/create",
            "GenresList": "services/genres/list",
            "GenresGet": "services/genres/get",
            "GenresUpdate": "services/genres/update",
            "GenresDelete": "services/genres/delete",
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, shared_layer_stack, auth_layer_stack).fn

    def attach_to_api(self, api: ApiGatewayStack):
        genres = api.api.root.add_resource("genres")
        genre_id = genres.add_resource("{id}")

        genres.add_method("POST", apigw.LambdaIntegration(self.lambdas["GenresCreate"]), **api.auth_kwargs)
        genres.add_method("GET", apigw.LambdaIntegration(self.lambdas["GenresList"]), **api.auth_kwargs)

        genre_id.add_method("GET", apigw.LambdaIntegration(self.lambdas["GenresGet"]), **api.auth_kwargs)
        genre_id.add_method("PATCH", apigw.LambdaIntegration(self.lambdas["GenresUpdate"]), **api.auth_kwargs)
        genre_id.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["GenresDelete"]), **api.auth_kwargs)