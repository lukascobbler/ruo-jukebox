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

        artists_create = mk_lambda("ArtistsCreate", "services/music_service/artists/create", env, dynamo_db, s3)
        artists_list   = mk_lambda("ArtistsList",   "services/music_service/artists/list", env, dynamo_db, s3)
        artists_get    = mk_lambda("ArtistsGet",    "services/music_service/artists/get", env, dynamo_db, s3)
        artists_update = mk_lambda("ArtistsUpdate", "services/music_service/artists/update", env, dynamo_db, s3)
        artists_delete = mk_lambda("ArtistsDelete", "services/music_service/artists/delete", env, dynamo_db, s3)

        artists = api_gateway.api.root.add_resource("artists")
        artist_id = artists.add_resource("{id}")

        artists.add_method(
            "POST",
            apigw.LambdaIntegration(artists_create),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )  # todo admin: check group in lambda
        artists.add_method(
            "GET",
            apigw.LambdaIntegration(artists_list),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )

        artist_id.add_method(
            "GET",
            apigw.LambdaIntegration(artists_get),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        artist_id.add_method(
            "PATCH",
            apigw.LambdaIntegration(artists_update),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )
        artist_id.add_method(
            "DELETE",
            apigw.LambdaIntegration(artists_delete),
            **auth_kwargs,
            authorization_type=AuthorizationType.COGNITO,
            authorizer=authorizer
        )