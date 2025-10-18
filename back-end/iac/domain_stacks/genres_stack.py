from constructs import Construct
from aws_cdk.aws_apigateway import AuthorizationType
from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
)

from iac.api_gateway_stack import ApiGatewayStack
from iac.cognito_stack import CognitoStack
from iac.common import mk_lambda
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack


class GenresStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 cognito: CognitoStack, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_endpoints(cognito, dynamo_db, s3, api_gateway, env)

    def _init_endpoints(self, cognito, dynamo_db, s3, api_gateway, env):
        genres_create = mk_lambda(self, "GenresCreate", "services/genres/create", env, dynamo_db, s3)
        genres_list   = mk_lambda(self, "GenresList",   "services/genres/list", env, dynamo_db, s3)
        genres_get    = mk_lambda(self, "GenresGet",    "services/genres/get", env, dynamo_db, s3)
        genres_update = mk_lambda(self, "GenresUpdate", "services/genres/update", env, dynamo_db, s3)
        genres_delete = mk_lambda(self, "GenresDelete", "services/genres/delete", env, dynamo_db, s3)

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

