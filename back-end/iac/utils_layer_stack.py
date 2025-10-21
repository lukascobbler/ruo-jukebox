from aws_cdk import Stack, aws_lambda as _lambda, aws_lambda
from constructs import Construct


class UtilsLayerStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.utils_layer = _lambda.LayerVersion(
            self, "UtilsLayer",
            code=_lambda.Code.from_asset("utils_layer"),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11],
            description="Utils python libraries shared across lambda functions"
        )