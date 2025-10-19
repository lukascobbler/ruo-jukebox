from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared_layer_stack import SharedLayerStack
from aws_cdk import Stack, aws_apigateway as apigw
from iac.api_gateway_stack import ApiGatewayStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack
from constructs import Construct


class AlbumsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack, s3: S3Stack, shared_layer_stack: SharedLayerStack,
                 environment, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.lambdas = {}
        self._create_lambdas(dynamo_db, s3, shared_layer_stack, environment)

    def _create_lambdas(self, dynamo_db, s3, shared_layer_stack, env):
        lambda_defs = {
            "AlbumsCreate": "services/albums/create",
            "AlbumsList": "services/albums/list",
            "AlbumsGet": "services/albums/get",
            "AlbumsUpdate": "services/albums/update",
            "AlbumsDelete": "services/albums/delete",
            "AlbumsCoverInit": "services/albums/init_cover_upload",
            "AlbumsCoverDone": "services/albums/complete_cover"
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, shared_layer_stack).fn

    def attach_to_api(self, api: ApiGatewayStack):
        albums = api.api.root.add_resource("albums")
        album_id = albums.add_resource("{id}")

        albums.add_method("POST", apigw.LambdaIntegration(self.lambdas["AlbumsCreate"]), **api.auth_kwargs)
        albums.add_method("GET", apigw.LambdaIntegration(self.lambdas["AlbumsList"]), **api.auth_kwargs)

        albums.add_resource("init-cover-upload").add_method("POST", apigw.LambdaIntegration(self.lambdas["AlbumsCoverInit"]), **api.auth_kwargs)
        albums.add_resource("complete-cover").add_method("POST", apigw.LambdaIntegration(self.lambdas["AlbumsCoverDone"]), **api.auth_kwargs)

        album_id.add_method("GET", apigw.LambdaIntegration(self.lambdas["AlbumsGet"]), **api.auth_kwargs)
        album_id.add_method("PATCH", apigw.LambdaIntegration(self.lambdas["AlbumsUpdate"]), **api.auth_kwargs)
        album_id.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["AlbumsDelete"]), **api.auth_kwargs)
