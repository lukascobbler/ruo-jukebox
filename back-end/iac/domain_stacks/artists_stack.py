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
                 dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)
        self._init_endpoints(dynamo_db, s3, api_gateway, env)

    def _init_endpoints(self, dynamo_db, s3, api_gateway, env):
        artists_create = mk_lambda(self, "ArtistsCreate", "services/artists/create", env, dynamo_db, s3)
        artists_list   = mk_lambda(self, "ArtistsList",   "services/artists/list", env, dynamo_db, s3)
        artists_get    = mk_lambda(self, "ArtistsGet",    "services/artists/get", env, dynamo_db, s3)
        artists_update = mk_lambda(self, "ArtistsUpdate", "services/artists/update", env, dynamo_db, s3)
        artists_delete = mk_lambda(self, "ArtistsDelete", "services/artists/delete", env, dynamo_db, s3)

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