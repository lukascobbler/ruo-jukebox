from iac.custom_constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk import NestedStack, aws_apigateway as apigw
from iac.layers.utils_layer_stack import UtilsLayerStack
from iac.shared.api_gateway_stack import ApiGatewayStack
from iac.layers.libs_layer_stack import LibsLayerStack
from iac.layers.auth_layer_stack import AuthLayerStack
from iac.shared.dynamo_db_stack import DynamoDbStack
from iac.shared.s3_stack import S3Stack
from constructs import Construct
from aws_cdk import aws_sqs as sqs

class LyricsStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, dynamo_db: DynamoDbStack, s3: S3Stack, libs_layer_stack: LibsLayerStack,
                 auth_layer_stack: AuthLayerStack, utils_layer_stack: UtilsLayerStack, api_stack: ApiGatewayStack, environment, **kwargs):
        super().__init__(scope, stack_id, **kwargs)
        self.lambdas = {}
        self._create_lambdas(dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, environment)
        self._attach_to_api(api_stack)

    def _create_lambdas(self, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, env):
        lambda_defs = {
            "GetSongLyrics": "services/transcription/get",
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack).fn

    def _attach_to_api(self, api: ApiGatewayStack):
        lyrics = api.api.root.add_resource("lyrics")
        song_lyrics = lyrics.add_resource("{id}")

        song_lyrics.add_method("GET", apigw.LambdaIntegration(self.lambdas["GetSongLyrics"]), **api.auth_kwargs)