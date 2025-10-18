from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk import (Stack, aws_apigateway as apigw)
from iac.shared_layer_stack import SharedLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack
from constructs import Construct


class PlaylistsStack(Stack):
    def __init__(self, scope: Construct, id: str, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack, shared_layer_stack: SharedLayerStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_endpoints(dynamo_db, s3, api_gateway, shared_layer_stack, env)

    def _init_endpoints(self, dynamo_db, s3, api_gateway, shared_layer_stack, env):
        playlists_create = LambdaWithPermissions(self, "PlaylistsCreate", "services/playlists/create", env, dynamo_db, s3, shared_layer_stack).fn
        playlists_list_mine = LambdaWithPermissions(self, "PlaylistsListMine", "services/playlists/list_mine", env, dynamo_db, s3, shared_layer_stack).fn
        playlists_get = LambdaWithPermissions(self, "PlaylistsGet", "services/playlists/get", env, dynamo_db, s3, shared_layer_stack).fn
        playlists_update = LambdaWithPermissions(self, "PlaylistsUpdate", "services/playlists/update", env, dynamo_db, s3, shared_layer_stack).fn
        playlists_delete = LambdaWithPermissions(self, "PlaylistsDelete", "services/playlists/delete", env, dynamo_db, s3, shared_layer_stack).fn
        playlists_add_track = LambdaWithPermissions(self, "PlaylistsAddTrack", "services/playlists/add_track", env, dynamo_db, s3, shared_layer_stack).fn
        playlists_remove_track = LambdaWithPermissions(self, "PlaylistsRemoveTrack", "services/playlists/remove_track", env, dynamo_db, s3, shared_layer_stack).fn

        playlists = api_gateway.api.root.add_resource("playlists")
        pl_id = playlists.add_resource("{id}")
        pl_tracks = pl_id.add_resource("tracks")
        pl_trk_id = pl_tracks.add_resource("{trackId}")

        playlists.add_method(
            "POST",
            apigw.LambdaIntegration(playlists_create),
            **api_gateway.auth_kwargs
        )
        playlists.add_method(
            "GET",
            apigw.LambdaIntegration(playlists_list_mine),
            **api_gateway.auth_kwargs
        )
        pl_id.add_method(
            "GET",
            apigw.LambdaIntegration(playlists_get),
            **api_gateway.auth_kwargs
        )
        pl_id.add_method(
            "PATCH",
            apigw.LambdaIntegration(playlists_update),
            **api_gateway.auth_kwargs
        )
        pl_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(playlists_delete),
            **api_gateway.auth_kwargs
        )
        pl_tracks.add_method(
            "POST",
            apigw.LambdaIntegration(playlists_add_track),
            **api_gateway.auth_kwargs
        )
        pl_trk_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(playlists_remove_track),
            **api_gateway.auth_kwargs
        )
