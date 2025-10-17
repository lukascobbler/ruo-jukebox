from constructs import Construct
from aws_cdk.aws_apigateway import AuthorizationType
from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
)

from iac.api_gateway_stack import ApiGatewayStack
from iac.cognito_stack import CognitoStack
from iac.common import mk_lambda
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack


class RatingsStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 cognito: CognitoStack, dynamo_db: DynamoDbStack,
                 s3: S3Stack, api_gateway: ApiGatewayStack,
                 env, **kwargs):
        super().__init__(scope, id, **kwargs)

        auth_kwargs = cognito.auth_kwargs
        authorizer = cognito.authorizer

        subs_create = mk_lambda("SubsCreate",    "services/music_service/subscriptions/create", env, dynamo_db, s3)
        subs_list   = mk_lambda("SubsListMine",  "services/music_service/subscriptions/list_mine", env, dynamo_db, s3)
        subs_delete = mk_lambda("SubsDelete",    "services/music_service/subscriptions/delete", env, dynamo_db, s3)
