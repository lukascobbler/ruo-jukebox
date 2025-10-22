from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk import (Stack, aws_apigateway as apigw)
from iac.libs_layer_stack import LibsLayerStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.utils_layer_stack import UtilsLayerStack
from iac.auth_layer_stack import AuthLayerStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack
from constructs import Construct


class ArtistsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack, s3: S3Stack, libs_layer_stack: LibsLayerStack, auth_layer_stack: AuthLayerStack,
                 utils_layer_stack: UtilsLayerStack, api_stack: ApiGatewayStack,
                 environment, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.lambdas = {}
        self._create_lambdas(dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, environment)
        self._attach_to_api(api_stack)

    def _create_lambdas(self, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, env):
        lambda_defs = {
            "ArtistsList": "services/artists/list",
            "ArtistsGet": "services/artists/get",
            "ArtistsUpdate": "services/artists/update",
            "ArtistsDelete": "services/artists/delete",
            "ArtistsInitUpload": "services/artists/init_upload",
            "ArtistsCompleteUpload": "services/artists/complete_upload",
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack).fn

    def _attach_to_api(self, api_gateway: ApiGatewayStack):
        artists = api_gateway.api.root.add_resource("artists")
        artist_id = artists.add_resource("{id}")

        artists.add_method("GET", apigw.LambdaIntegration(self.lambdas["ArtistsList"]), **api_gateway.auth_kwargs)
        artists.add_resource("init-upload").add_method("POST", apigw.LambdaIntegration(self.lambdas["ArtistsInitUpload"]), **api_gateway.auth_kwargs)
        artists.add_resource("complete-upload").add_method("POST", apigw.LambdaIntegration(self.lambdas["ArtistsCompleteUpload"]), **api_gateway.auth_kwargs)

        artist_id.add_method("GET", apigw.LambdaIntegration(self.lambdas["ArtistsGet"]), **api_gateway.auth_kwargs)
        artist_id.add_method("PATCH", apigw.LambdaIntegration(self.lambdas["ArtistsUpdate"]), **api_gateway.auth_kwargs)
        artist_id.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["ArtistsDelete"]), **api_gateway.auth_kwargs)
