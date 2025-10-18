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


class PlaylistsStack(Stack):
    def __init__(self, scope: Construct, id: str, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_endpoints(dynamo_db, s3, api_gateway, env)

    def _init_endpoints(self, dynamo_db, s3, api_gateway, env):
        playlists_create = mk_lambda(self, "PlaylistsCreate", "services/playlists/create", env, dynamo_db, s3)
        playlists_list_mine = mk_lambda(self, "PlaylistsListMine", "services/playlists/list_mine", env, dynamo_db, s3)
        playlists_get = mk_lambda(self, "PlaylistsGet", "services/playlists/get", env, dynamo_db, s3)
        playlists_update = mk_lambda(self, "PlaylistsUpdate", "services/playlists/update", env, dynamo_db, s3)
        playlists_delete = mk_lambda(self, "PlaylistsDelete", "services/playlists/delete", env, dynamo_db, s3)
        playlists_add_track = mk_lambda(self, "PlaylistsAddTrack", "services/playlists/add_track", env, dynamo_db, s3)
        playlists_remove_track = mk_lambda(self, "PlaylistsRemoveTrack", "services/playlists/remove_track", env, dynamo_db, s3)

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

