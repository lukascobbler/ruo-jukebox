from aws_cdk import Stack, aws_lambda
from constructs import Construct


class SharedLayerStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.shared_layer = aws_lambda.LayerVersion(
            self, "SharedLayer",
            layer_version_name="shared_layer",
            code=aws_lambda.Code.from_asset("shared_layer", asset_hash="shared_layer_v1"),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11],
            description="Shared dependencies for all lambdas"
        )
