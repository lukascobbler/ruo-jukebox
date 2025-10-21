from iac.dynamo_db_stack import DynamoDbStack
from constructs import Construct
from aws_cdk import Stack


class InteractionsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 dynamo_db: DynamoDbStack,
                 environment, **kwargs):
        super().__init__(scope, id, **kwargs)
