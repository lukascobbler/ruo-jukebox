from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared_layer_stack import SharedLayerStack
from aws_cdk import Stack, aws_apigateway as apigw
from iac.api_gateway_stack import ApiGatewayStack
from iac.utils_layer_stack import UtilsLayerStack
from iac.auth_layer_stack import AuthLayerStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack
from constructs import Construct


class SongsStack(Stack):
    def __init__(self, scope: Construct, id: str, dynamo_db: DynamoDbStack, s3: S3Stack, shared_layer_stack: SharedLayerStack,
                 auth_layer_stack: AuthLayerStack, utils_layer_stack: UtilsLayerStack, api_stack: ApiGatewayStack, environment, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.lambdas = {}
        self._create_lambdas(dynamo_db, s3, shared_layer_stack, auth_layer_stack, utils_layer_stack, environment)
        self._attach_to_api(api_stack)

    def _create_lambdas(self, dynamo_db, s3, shared_layer_stack, auth_layer_stack, utils_layer_stack, env):
        lambda_defs = {
            "SongInitUpload": "services/songs/init_upload",
            "SongCompleteUpload": "services/songs/complete_upload",
            "SongList": "services/songs/list",
            "SongGet": "services/songs/get",
            "SongUpdate": "services/songs/update",
            "SongDelete": "services/songs/delete",
            "SongRatingPut": "services/song-ratings/put",
            "SongRatingDelete": "services/song-ratings/delete"
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, shared_layer_stack, auth_layer_stack, utils_layer_stack).fn

    def _attach_to_api(self, api: ApiGatewayStack):
        song = api.api.root.add_resource("song")
        song_id = song.add_resource("{id}")
        rating = song_id.add_resource("rating")

        song.add_resource("init-upload").add_method("POST", apigw.LambdaIntegration(self.lambdas["SongInitUpload"]), **api.auth_kwargs)
        song.add_resource("complete-upload").add_method("POST", apigw.LambdaIntegration(self.lambdas["SongCompleteUpload"]), **api.auth_kwargs)
        song.add_method("GET", apigw.LambdaIntegration(self.lambdas["SongList"]), **api.auth_kwargs)

        song_id.add_method("GET", apigw.LambdaIntegration(self.lambdas["SongGet"]), **api.auth_kwargs)
        song_id.add_method("PATCH", apigw.LambdaIntegration(self.lambdas["SongUpdate"]), **api.auth_kwargs)
        song_id.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["SongDelete"]), **api.auth_kwargs)

        rating.add_method("PUT", apigw.LambdaIntegration(self.lambdas["SongRatingPut"]), **api.auth_kwargs)
        rating.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["SongRatingDelete"]), **api.auth_kwargs)
