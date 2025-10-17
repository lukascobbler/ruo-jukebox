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


class RatingsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 cognito: CognitoStack, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)

        auth_kwargs = cognito.auth_kwargs
        authorizer = cognito.authorizer

        genres_create = mk_lambda("GenresCreate", "services/music_service/genres/create", env, dynamo_db, s3)
        genres_list   = mk_lambda("GenresList",   "services/music_service/genres/list", env, dynamo_db, s3)
        genres_get    = mk_lambda("GenresGet",    "services/music_service/genres/get", env, dynamo_db, s3)
        genres_update = mk_lambda("GenresUpdate", "services/music_service/genres/update", env, dynamo_db, s3)
        genres_delete = mk_lambda("GenresDelete", "services/music_service/genres/delete", env, dynamo_db, s3)

        genres = api_gateway.api.root.add_resource("genres")
        genre_id = genres.add_resource("{id}")

        genres.add_method(
            "POST",
            apigw.LambdaIntegration(genres_create),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        genres.add_method(
            "GET",
            apigw.LambdaIntegration(genres_list),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )

        genre_id.add_method(
            "GET",
            apigw.LambdaIntegration(genres_get),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        genre_id.add_method(
            "PATCH",
            apigw.LambdaIntegration(genres_update),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        genre_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(genres_delete),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )

