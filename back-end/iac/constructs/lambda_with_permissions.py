from iac.shared_layer_stack import SharedLayerStack
from iac.dynamo_db_stack import DynamoDbStack
from aws_cdk import Duration, aws_lambda
from aws_cdk.aws_dynamodb import Table
from constructs import Construct
from iac.s3_stack import S3Stack

class LambdaWithPermissions(Construct):
    def __init__(self, scope: Construct, id: str, path: str, env: dict, dynamo_db: DynamoDbStack, s3: S3Stack, shared_layer_stack: SharedLayerStack, extra_env: dict | None = None):
        super().__init__(scope, id)
        env = {**env, **(extra_env or {})}
        self.fn = aws_lambda.Function(
            self, "LambdaFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="lambda.lambda_handler",
            code=aws_lambda.Code.from_asset(path),
            layers=[shared_layer_stack.shared_layer],
            environment=env,
            timeout=Duration.seconds(15),
            memory_size=256,
        )
        # grants TODO right now everyone gets everything
        s3.audio_bucket.grant_read_write(self.fn)
        s3.images_bucket.grant_read_write(self.fn)
        s3.transcripts_bucket.grant_read_write(self.fn)
        for table in (t for t in vars(dynamo_db).values() if isinstance(t, Table)):
            table.grant_read_write_data(self.fn)
