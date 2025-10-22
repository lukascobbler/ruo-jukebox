from aws_cdk import NestedStack, aws_lambda
from constructs import Construct


class AuthLayerStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, **kwargs) -> None:
        super().__init__(scope, stack_id, **kwargs)

        self.auth_layer = aws_lambda.LayerVersion(
            self, "AuthLayer",
            code=aws_lambda.Code.from_asset("auth_layer"),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11],
            description="Authorization layer"
        )
