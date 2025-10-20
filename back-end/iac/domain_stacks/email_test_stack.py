from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from iac.shared_layer_stack import SharedLayerStack
from aws_cdk import Stack, aws_apigateway as apigw
from iac.api_gateway_stack import ApiGatewayStack
from iac.auth_layer_stack import AuthLayerStack
from iac.dynamo_db_stack import DynamoDbStack
from iac.email_stack import EmailStack
from iac.s3_stack import S3Stack
from constructs import Construct


class EmailTestStack(Stack):
    def __init__(self, scope: Construct, id: str, dynamo_db: DynamoDbStack, s3: S3Stack, shared_layer_stack: SharedLayerStack, auth_layer_stack: AuthLayerStack,
                 api_stack: ApiGatewayStack, email_stack: EmailStack, environment, **kwargs):
        super().__init__(scope, id, **kwargs)

        send_email_lambda = LambdaWithPermissions(self, "SendEmailLambda", "services/email_test/send", environment, dynamo_db, s3, shared_layer_stack, auth_layer_stack).fn

        send_email_lambda.role.add_managed_policy(email_stack.send_policy)
        email_send = api_stack.api.root.add_resource("email").add_resource("send")
        email_send.add_method("POST", apigw.LambdaIntegration(send_email_lambda), **api_stack.auth_kwargs)
