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


class ArtistsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 cognito: CognitoStack, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)

        auth_kwargs = cognito.auth_kwargs
        authorizer = cognito.authorizer

        albums_create = mk_lambda("AlbumsCreate", "albums/create", env, dynamo_db, s3)
        albums_list = mk_lambda("AlbumsList", "albums/list", env, dynamo_db, s3)
        albums_get = mk_lambda("AlbumsGet", "albums/get", env, dynamo_db, s3)
        albums_update = mk_lambda("AlbumsUpdate", "albums/update", env, dynamo_db, s3)
        albums_delete = mk_lambda("AlbumsDelete", "albums/delete", env, dynamo_db, s3)
        albums_cov_init = mk_lambda("AlbumsCoverInit", "albums/init_cover_upload", env, dynamo_db, s3)
        albums_cov_done = mk_lambda("AlbumsCoverDone", "albums/complete_cover", env, dynamo_db, s3)

        albums = api_gateway.api.root.add_resource("albums")
        album_id = albums.add_resource("{id}")

        albums.add_method(
            "POST",
            apigw.LambdaIntegration(albums_create),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        albums.add_method(
            "GET",
            apigw.LambdaIntegration(albums_list),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        albums.add_resource("init-cover-upload").add_method(
            "POST",
            apigw.LambdaIntegration(albums_cov_init),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        albums.add_resource("complete-cover").add_method(
            "POST",
            apigw.LambdaIntegration(albums_cov_done),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )

        album_id.add_method(
            "GET",
            apigw.LambdaIntegration(albums_get),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        album_id.add_method(
            "PATCH",
            apigw.LambdaIntegration(albums_update),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        album_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(albums_delete),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )