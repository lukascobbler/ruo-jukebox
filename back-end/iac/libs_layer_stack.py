from aws_cdk import Stack, aws_lambda
from constructs import Construct


class LibsLayerStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.libs_layer = aws_lambda.LayerVersion(
            self, "LibsLayer",
            layer_version_name="libs_layer",
            code=aws_lambda.Code.from_asset("libs_layer", asset_hash="libs_layer_v1"),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11],
            description="Libs dependencies shared for all lambdas"
        )
