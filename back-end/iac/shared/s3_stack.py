from aws_cdk import NestedStack, RemovalPolicy, PhysicalName, aws_s3 as s3
from constructs import Construct


class S3Stack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)

        common_cors = [
            s3.CorsRule(
                allowed_methods=[
                    s3.HttpMethods.GET,
                    s3.HttpMethods.PUT,
                    s3.HttpMethods.POST,
                    s3.HttpMethods.DELETE,
                    s3.HttpMethods.HEAD
                ],
                allowed_origins=["*"],  # TODO change cors everywhere
                allowed_headers=["*"],
                max_age=3000
            )
        ]

        # songs bucket
        self.audio_bucket = s3.Bucket(
            self, "AudioBucket",
            bucket_name=PhysicalName.GENERATE_IF_NEEDED,
            cors=common_cors,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            event_bridge_enabled=True
        )

        # images bucket
        self.images_bucket = s3.Bucket(
            self, "ImagesBucket",
            bucket_name=PhysicalName.GENERATE_IF_NEEDED,
            cors=common_cors,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # transcripts bucket
        self.transcripts_bucket = s3.Bucket(
            self, "TranscriptsBucket",
            bucket_name=PhysicalName.GENERATE_IF_NEEDED,
            cors=common_cors,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )