from iac.shared.dynamo_db_stack import DynamoDbStack
from constructs import Construct
from aws_cdk import NestedStack


class InteractionsStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str,
                 dynamo_db: DynamoDbStack,
                 environment, **kwargs):
        super().__init__(scope, stack_id, **kwargs)
