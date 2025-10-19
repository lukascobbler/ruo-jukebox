from iac.auth_layer_stack import AuthLayerStack
from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk import (Stack, aws_apigateway as apigw)
from iac.shared_layer_stack import SharedLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack
from constructs import Construct


class ArtistsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack, s3: S3Stack, shared_layer_stack: SharedLayerStack, auth_layer_stack: AuthLayerStack,
                 environment, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.lambdas = {}
        self._create_lambdas(dynamo_db, s3, shared_layer_stack, auth_layer_stack, environment)

    def _create_lambdas(self, dynamo_db, s3, shared_layer_stack, auth_layer_stack, env):
        lambda_defs = {
            "ArtistsCreate": "services/artists/create",
            "ArtistsList": "services/artists/list",
            "ArtistsGet": "services/artists/get",
            "ArtistsUpdate": "services/artists/update",
            "ArtistsDelete": "services/artists/delete",
            "ArtistsPicInit": "services/artists/picture/init_upload",
            "ArtistsPicComplete": "services/artists/picture/complete_upload",
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, shared_layer_stack, auth_layer_stack).fn

    def attach_to_api(self, api_gateway: ApiGatewayStack):
        artists = api_gateway.api.root.add_resource("artists")
        artist_id = artists.add_resource("{id}")

        artists.add_method("POST", apigw.LambdaIntegration(self.lambdas["ArtistsCreate"]), **api_gateway.auth_kwargs)
        artists.add_method("GET", apigw.LambdaIntegration(self.lambdas["ArtistsList"]), **api_gateway.auth_kwargs)

        artist_id.add_method("GET", apigw.LambdaIntegration(self.lambdas["ArtistsGet"]), **api_gateway.auth_kwargs)
        artist_id.add_method("PATCH", apigw.LambdaIntegration(self.lambdas["ArtistsUpdate"]), **api_gateway.auth_kwargs)
        artist_id.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["ArtistsDelete"]), **api_gateway.auth_kwargs)

        picture = artist_id.add_resource("picture")
        picture.add_resource("init_upload").add_method(
            "POST", apigw.LambdaIntegration(self.lambdas["ArtistsPicInit"]), **api_gateway.auth_kwargs
        )
        picture.add_resource("complete_upload").add_method(
            "POST", apigw.LambdaIntegration(self.lambdas["ArtistsPicComplete"]), **api_gateway.auth_kwargs
        )