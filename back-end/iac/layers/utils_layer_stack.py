from aws_cdk import NestedStack, aws_lambda
from constructs import Construct


class UtilsLayerStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, **kwargs) -> None:
        super().__init__(scope, stack_id, **kwargs)

        self.utils_layer = aws_lambda.LayerVersion(
            self, "UtilsLayer",
            code=aws_lambda.Code.from_asset("utils_layer"),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11],
            description="Utils python libraries shared across lambda functions"
        )
