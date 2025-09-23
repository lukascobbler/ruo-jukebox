from aws_cdk import Stack, aws_dynamodb as dynamodb, RemovalPolicy
from constructs import Construct

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.table = dynamodb.Table(
            self, "DemoTable",
            partition_key=dynamodb.Attribute(name="name", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="seq", type=dynamodb.AttributeType.NUMBER),
            removal_policy=RemovalPolicy.DESTROY
        )
