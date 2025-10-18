from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk import (Stack, aws_apigateway as apigw)
from iac.shared_layer_stack import SharedLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack
from constructs import Construct


class ArtistsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack, shared_layer_stack: SharedLayerStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_endpoints(dynamo_db, s3, api_gateway, shared_layer_stack, env)

    def _init_endpoints(self, dynamo_db, s3, api_gateway, shared_layer_stack, env):
        artists_create = LambdaWithPermissions(self, "ArtistsCreate", "services/artists/create", env, dynamo_db, s3, shared_layer_stack).fn
        artists_list = LambdaWithPermissions(self, "ArtistsList", "services/artists/list", env, dynamo_db, s3, shared_layer_stack).fn
        artists_get = LambdaWithPermissions(self, "ArtistsGet", "services/artists/get", env, dynamo_db, s3, shared_layer_stack).fn
        artists_update = LambdaWithPermissions(self, "ArtistsUpdate", "services/artists/update", env, dynamo_db, s3, shared_layer_stack).fn
        artists_delete = LambdaWithPermissions(self, "ArtistsDelete", "services/artists/delete", env, dynamo_db, s3, shared_layer_stack).fn

        artists = api_gateway.api.root.add_resource("artists")
        artist_id = artists.add_resource("{id}")

        artists.add_method(
            "POST",
            apigw.LambdaIntegration(artists_create),
            **api_gateway.auth_kwargs
        )  # todo admin: check group in lambda
        artists.add_method(
            "GET",
            apigw.LambdaIntegration(artists_list),
            **api_gateway.auth_kwargs
        )

        artist_id.add_method(
            "GET",
            apigw.LambdaIntegration(artists_get),
            **api_gateway.auth_kwargs
        )
        artist_id.add_method(
            "PATCH",
            apigw.LambdaIntegration(artists_update),
            **api_gateway.auth_kwargs
        )
        artist_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(artists_delete),
            **api_gateway.auth_kwargs
        )
