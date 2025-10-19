from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared_layer_stack import SharedLayerStack
from aws_cdk import Stack, aws_apigateway as apigw
from iac.api_gateway_stack import ApiGatewayStack
from iac.dynamo_db_stack import DynamoDbStack
from constructs import Construct
from iac.s3_stack import S3Stack


class PlaylistsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack, s3: S3Stack, shared_layer_stack: SharedLayerStack,
                 environment, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.lambdas = {}
        self._create_lambdas(dynamo_db, s3, shared_layer_stack, environment)

    def _create_lambdas(self, dynamo_db, s3, shared_layer_stack, env):
        lambda_defs = {
            "PlaylistsCreate": "services/playlists/create",
            "PlaylistsListMine": "services/playlists/list_mine",
            "PlaylistsGet": "services/playlists/get",
            "PlaylistsUpdate": "services/playlists/update",
            "PlaylistsDelete": "services/playlists/delete",
            "PlaylistsAddSong": "services/playlists/add_song",
            "PlaylistsRemoveSong": "services/playlists/remove_song"
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, shared_layer_stack).fn

    def attach_to_api(self, api: ApiGatewayStack):
        playlists = api.api.root.add_resource("playlists")
        pl_id = playlists.add_resource("{id}")
        pl_songs = pl_id.add_resource("songs")
        pl_song_id = pl_songs.add_resource("{songId}")

        playlists.add_method("POST", apigw.LambdaIntegration(self.lambdas["PlaylistsCreate"]), **api.auth_kwargs)
        playlists.add_method("GET", apigw.LambdaIntegration(self.lambdas["PlaylistsListMine"]), **api.auth_kwargs)

        pl_id.add_method("GET", apigw.LambdaIntegration(self.lambdas["PlaylistsGet"]), **api.auth_kwargs)
        pl_id.add_method("PATCH", apigw.LambdaIntegration(self.lambdas["PlaylistsUpdate"]), **api.auth_kwargs)
        pl_id.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["PlaylistsDelete"]), **api.auth_kwargs)

        pl_songs.add_method("POST", apigw.LambdaIntegration(self.lambdas["PlaylistsAddSong"]), **api.auth_kwargs)
        pl_song_id.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["PlaylistsRemoveSong"]), **api.auth_kwargs)
