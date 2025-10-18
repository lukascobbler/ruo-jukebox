from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk import (Stack, aws_apigateway as apigw)
from iac.shared_layer_stack import SharedLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack
from constructs import Construct


class AlbumsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack, shared_layer_stack: SharedLayerStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_endpoints(dynamo_db, s3, api_gateway, shared_layer_stack, env)

    def _init_endpoints(self, dynamo_db, s3, api_gateway, shared_layer_stack, env):
        albums_create = LambdaWithPermissions(self, "AlbumsCreate", "services/albums/create", env, dynamo_db, s3, shared_layer_stack).fn
        albums_list = LambdaWithPermissions(self, "AlbumsList", "services/albums/list", env, dynamo_db, s3, shared_layer_stack).fn
        albums_get = LambdaWithPermissions(self, "AlbumsGet", "services/albums/get", env, dynamo_db, s3, shared_layer_stack).fn
        albums_update = LambdaWithPermissions(self, "AlbumsUpdate", "services/albums/update", env, dynamo_db, s3, shared_layer_stack).fn
        albums_delete = LambdaWithPermissions(self, "AlbumsDelete", "services/albums/delete", env, dynamo_db, s3, shared_layer_stack).fn
        albums_cov_init = LambdaWithPermissions(self, "AlbumsCoverInit", "services/albums/init_cover_upload", env, dynamo_db, s3, shared_layer_stack).fn
        albums_cov_done = LambdaWithPermissions(self, "AlbumsCoverDone", "services/albums/complete_cover", env, dynamo_db, s3, shared_layer_stack).fn

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
