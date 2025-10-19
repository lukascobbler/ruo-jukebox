from constructs import Construct
from aws_cdk import Stack, aws_lambda as _lambda


class AuthLayerStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.auth_layer = _lambda.LayerVersion(
            self, "AuthLayer",
            code=_lambda.Code.from_asset("auth_layer"),
            compatible_runtimes=_lambda.Runtime.PYTHON_3_11,
            description="Authorization layer"
        )