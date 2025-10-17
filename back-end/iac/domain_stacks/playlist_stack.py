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


class PlaylistStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 cognito: CognitoStack, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)

        auth_kwargs = cognito.auth_kwargs
        authorizer = cognito.authorizer

        playlists_create = mk_lambda("PlaylistsCreate", "services/music_service/playlists/create", env, dynamo_db, s3)
        playlists_list_mine = mk_lambda("PlaylistsListMine", "services/music_service/playlists/list_mine", env, dynamo_db, s3)
        playlists_get = mk_lambda("PlaylistsGet", "services/music_service/playlists/get", env, dynamo_db, s3)
        playlists_update = mk_lambda("PlaylistsUpdate", "services/music_service/playlists/update", env, dynamo_db, s3)
        playlists_delete = mk_lambda("PlaylistsDelete", "services/music_service/playlists/delete", env, dynamo_db, s3)
        playlists_add_track = mk_lambda("PlaylistsAddTrack", "services/music_service/playlists/add_track", env, dynamo_db, s3)
        playlists_remove_track = mk_lambda("PlaylistsRemoveTrack", "services/music_service/playlists/remove_track", env, dynamo_db, s3)

        playlists = api_gateway.api.root.add_resource("playlists")
        pl_id = playlists.add_resource("{id}")
        pl_tracks = pl_id.add_resource("tracks")
        pl_trk_id = pl_tracks.add_resource("{trackId}")

        playlists.add_method(
            "POST",
            apigw.LambdaIntegration(playlists_create),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        playlists.add_method(
            "GET",
            apigw.LambdaIntegration(playlists_list_mine),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        pl_id.add_method(
            "GET",
            apigw.LambdaIntegration(playlists_get),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        pl_id.add_method(
            "PATCH",
            apigw.LambdaIntegration(playlists_update),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        pl_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(playlists_delete),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        pl_tracks.add_method(
            "POST",
            apigw.LambdaIntegration(playlists_add_track),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        pl_trk_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(playlists_remove_track),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )

