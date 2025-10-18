from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk import (Stack, aws_apigateway as apigw)
from iac.shared_layer_stack import SharedLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.dynamo_db_stack import DynamoDbStack
from constructs import Construct
from iac.s3_stack import S3Stack


class GenresStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack, shared_layer_stack: SharedLayerStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_endpoints(dynamo_db, s3, api_gateway, shared_layer_stack, env)

    def _init_endpoints(self, dynamo_db, s3, api_gateway, shared_layer_stack, env):
        genres_create = LambdaWithPermissions(self, "GenresCreate", "services/genres/create", env, dynamo_db, s3, shared_layer_stack).fn
        genres_list = LambdaWithPermissions(self, "GenresList", "services/genres/list", env, dynamo_db, s3, shared_layer_stack).fn
        genres_get = LambdaWithPermissions(self, "GenresGet", "services/genres/get", env, dynamo_db, s3, shared_layer_stack).fn
        genres_update = LambdaWithPermissions(self, "GenresUpdate", "services/genres/update", env, dynamo_db, s3, shared_layer_stack).fn
        genres_delete = LambdaWithPermissions(self, "GenresDelete", "services/genres/delete", env, dynamo_db, s3, shared_layer_stack).fn

        genres = api_gateway.api.root.add_resource("genres")
        genre_id = genres.add_resource("{id}")

        genres.add_method(
            "POST",
            apigw.LambdaIntegration(genres_create),
            **api_gateway.auth_kwargs
        )
        genres.add_method(
            "GET",
            apigw.LambdaIntegration(genres_list),
            **api_gateway.auth_kwargs
        )

        genre_id.add_method(
            "GET",
            apigw.LambdaIntegration(genres_get),
            **api_gateway.auth_kwargs
        )
        genre_id.add_method(
            "PATCH",
            apigw.LambdaIntegration(genres_update),
            **api_gateway.auth_kwargs
        )
        genre_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(genres_delete),
            **api_gateway.auth_kwargs
        )
