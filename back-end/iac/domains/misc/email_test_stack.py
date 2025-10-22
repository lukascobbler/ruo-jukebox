from iac.custom_constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk import NestedStack, aws_apigateway as apigw
from iac.layers.utils_layer_stack import UtilsLayerStack
from iac.layers.libs_layer_stack import LibsLayerStack
from iac.layers.auth_layer_stack import AuthLayerStack
from iac.shared.dynamo_db_stack import DynamoDbStack
from iac.api_gateway_stack import ApiGatewayStack
from iac.shared.email_stack import EmailStack
from iac.shared.s3_stack import S3Stack
from constructs import Construct


class EmailTestStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, dynamo_db: DynamoDbStack, s3: S3Stack, libs_layer_stack: LibsLayerStack, auth_layer_stack: AuthLayerStack,
                 utils_layer_stack: UtilsLayerStack, api_stack: ApiGatewayStack, email_stack: EmailStack, environment, **kwargs):
        super().__init__(scope, stack_id, **kwargs)

        send_email_lambda = LambdaWithPermissions(self, "SendEmailLambda", "services/email_test/send", environment, dynamo_db, s3,
                                                  libs_layer_stack, auth_layer_stack, utils_layer_stack).fn

        send_email_lambda.role.add_managed_policy(email_stack.send_policy)
        email_send = api_stack.api.root.add_resource("email").add_resource("send")
        email_send.add_method("POST", apigw.LambdaIntegration(send_email_lambda), **api_stack.auth_kwargs)
