from iac.custom_constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk import NestedStack, aws_apigateway as apigw
from iac.layers.utils_layer_stack import UtilsLayerStack
from iac.shared.api_gateway_stack import ApiGatewayStack
from iac.layers.libs_layer_stack import LibsLayerStack
from iac.layers.auth_layer_stack import AuthLayerStack
from iac.shared.dynamo_db_stack import DynamoDbStack
from iac.shared.s3_stack import S3Stack
from aws_cdk import aws_sqs as sqs
from constructs import Construct


class AlbumsStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str,
                 dynamo_db: DynamoDbStack, s3: S3Stack, libs_layer_stack: LibsLayerStack, auth_layer_stack: AuthLayerStack,
                 utils_layer_stack: UtilsLayerStack, api_stack: ApiGatewayStack, environment, branch: str, subs_queue: sqs.IQueue, feed_queue: sqs.IQueue, **kwargs):
        super().__init__(scope, stack_id, **kwargs)
        self.lambdas = {}
        environment = {**environment, "SUB_QUEUE_URL": subs_queue.queue_url}
        environment = {**environment, "FEED_QUEUE_URL": feed_queue.queue_url}
        self._create_lambdas(dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, environment, branch)
        self._attach_to_api(api_stack)
        subs_queue.grant_send_messages(self.lambdas["AlbumsCompleteUpload"])
        feed_queue.grant_send_messages(self.lambdas["AlbumsCompleteUpload"])

    def _create_lambdas(self, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, env, branch):
        lambda_defs = {
            "AlbumsList": "services/albums/list",
            "AlbumsGet": "services/albums/get",
            "AlbumsUpdate": "services/albums/update",
            "AlbumsDelete": "services/albums/delete",
            "AlbumsInitUpload": "services/albums/init_upload",
            "AlbumsCompleteUpload": "services/albums/complete_upload"
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, libs_layer_stack, auth_layer_stack, utils_layer_stack, branch).fn

    def _attach_to_api(self, api: ApiGatewayStack):
        albums = api.api.root.add_resource("album")
        album_id = albums.add_resource("{id}")

        albums.add_method("GET", apigw.LambdaIntegration(self.lambdas["AlbumsList"]), **api.auth_kwargs)

        albums.add_resource("init-upload").add_method("POST", apigw.LambdaIntegration(self.lambdas["AlbumsInitUpload"]), **api.auth_kwargs)
        albums.add_resource("complete-upload").add_method("POST", apigw.LambdaIntegration(self.lambdas["AlbumsCompleteUpload"]), **api.auth_kwargs)

        album_id.add_method("GET", apigw.LambdaIntegration(self.lambdas["AlbumsGet"]), **api.auth_kwargs)
        album_id.add_method("PATCH", apigw.LambdaIntegration(self.lambdas["AlbumsUpdate"]), **api.auth_kwargs)  # todo
        album_id.add_method("DELETE", apigw.LambdaIntegration(self.lambdas["AlbumsDelete"]), **api.auth_kwargs)  # todo
