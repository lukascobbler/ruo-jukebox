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


class AlbumsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_endpoints(dynamo_db, s3, api_gateway, env)

    def _init_endpoints(self, dynamo_db, s3, api_gateway, env):
        albums_create = mk_lambda(self, "AlbumsCreate", "services/albums/create", env, dynamo_db, s3)
        albums_list = mk_lambda(self, "AlbumsList", "services/albums/list", env, dynamo_db, s3)
        albums_get = mk_lambda(self, "AlbumsGet", "services/albums/get", env, dynamo_db, s3)
        albums_update = mk_lambda(self, "AlbumsUpdate", "services/albums/update", env, dynamo_db, s3)
        albums_delete = mk_lambda(self, "AlbumsDelete", "services/albums/delete", env, dynamo_db, s3)
        albums_cov_init = mk_lambda(self, "AlbumsCoverInit", "services/albums/init_cover_upload", env, dynamo_db, s3)
        albums_cov_done = mk_lambda(self, "AlbumsCoverDone", "services/albums/complete_cover", env, dynamo_db, s3)

        albums = api_gateway.api.root.add_resource("albums")
        album_id = albums.add_resource("{id}")

        albums.add_method(
            "POST",
            apigw.LambdaIntegration(albums_create),
            **api_gateway.auth_kwargs
        )
        albums.add_method(
            "GET",
            apigw.LambdaIntegration(albums_list),
            **api_gateway.auth_kwargs
        )
        albums.add_resource("init-cover-upload").add_method(
            "POST",
            apigw.LambdaIntegration(albums_cov_init),
            **api_gateway.auth_kwargs
        )
        albums.add_resource("complete-cover").add_method(
            "POST",
            apigw.LambdaIntegration(albums_cov_done),
            **api_gateway.auth_kwargs
        )

        album_id.add_method(
            "GET",
            apigw.LambdaIntegration(albums_get),
            **api_gateway.auth_kwargs
        )
        album_id.add_method(
            "PATCH",
            apigw.LambdaIntegration(albums_update),
            **api_gateway.auth_kwargs
        )
        album_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(albums_delete),
            **api_gateway.auth_kwargs
        )