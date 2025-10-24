from aws_cdk import NestedStack, aws_lambda
from constructs import Construct


class LibsLayerStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)

        self.libs_layer = aws_lambda.LayerVersion(
            self, "LibsLayer",
            layer_version_name="libs_layer",
            code=aws_lambda.Code.from_asset("libs_layer", asset_hash="libs_layer_v2"),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11],
            description="Libs dependencies shared for all lambdas"
        )
