from aws_cdk import aws_events as events, aws_events_targets as targets
from iac.shared.transcription_stack import TranscriptionStack
from iac.layers.utils_layer_stack import UtilsLayerStack
from iac.layers.libs_layer_stack import LibsLayerStack
from iac.layers.auth_layer_stack import AuthLayerStack
from iac.shared.dynamo_db_stack import DynamoDbStack
from iac.shared.cognito_stack import CognitoStack
from iac.shared.s3_stack import S3Stack
from constructs import Construct
from aws_cdk import NestedStack
import json


class SharedResourcesStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, branch: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)

        self.cognito_stack = CognitoStack(self, "CognitoStack", branch)
        self.utils_layer_stack = UtilsLayerStack(self, "UtilsLayerStack")
        self.auth_layer_stack = AuthLayerStack(self, "AuthLayerStack")
        self.libs_layer_stack = LibsLayerStack(self, "LibsLayerStack")
        self.dynamo_db_stack = DynamoDbStack(self, "DynamoDbStack", branch)
        self.s3_stack = S3Stack(self, "S3Stack")

        self.env_vars = {
            "AUDIO_BUCKET": self.s3_stack.audio_bucket.bucket_name,
            "IMAGES_BUCKET": self.s3_stack.images_bucket.bucket_name,
            "TRANSCRIPTS_BUCKET": self.s3_stack.transcripts_bucket.bucket_name,
            "CONTENT_TABLE": self.dynamo_db_stack.content.table_name,
            "USERDATA_TABLE": self.dynamo_db_stack.userdata.table_name,
            "INTERACTIONS_TABLE": self.dynamo_db_stack.interactions.table_name,
            "FEED_TABLE": self.dynamo_db_stack.feed.table_name,
            "USER_POOL_ID": self.cognito_stack.user_pool.user_pool_id,
            "USER_POOL_CLIENT_ID": self.cognito_stack.app_client.user_pool_client_id,
            "S3_ENDPOINT_URL": f"https://s3.{self.region}.amazonaws.com",
            "REGION": self.region,
            "FROM_EMAIL": "noreply@jb.moma.rs",
            "CORS_HEADERS": json.dumps({
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST,PUT,PATCH,DELETE",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*"
            })
        }

        self.transcription_stack = TranscriptionStack(self, "TranscriptionsStack", self.s3_stack, self.env_vars)

        rule = events.Rule(
            self, "AudioObjectCreatedRule",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={
                    "bucket": {"name": [self.s3_stack.audio_bucket.bucket_name]},
                    "object": {"key": [{"prefix": "songs/"}]}
                }
            )
        )

        rule.add_target(targets.LambdaFunction(self.transcription_stack.producer_lambda))
