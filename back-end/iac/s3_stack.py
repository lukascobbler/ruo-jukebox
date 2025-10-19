from aws_cdk import Stack, RemovalPolicy, PhysicalName, aws_s3 as s3
from constructs import Construct


class S3Stack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # songs bucket
        self.audio_bucket = s3.Bucket(
            self, "AudioBucket",
            bucket_name=PhysicalName.GENERATE_IF_NEEDED,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.PUT, s3.HttpMethods.GET, s3.HttpMethods.HEAD, s3.HttpMethods.DELETE],
                allowed_origins=["*"],   # TODO change cors everywhere
                allowed_headers=["*"],
                max_age=3000
            )],
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # images bucket
        self.images_bucket = s3.Bucket(
            self, "ImagesBucket",
            bucket_name=PhysicalName.GENERATE_IF_NEEDED,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.PUT, s3.HttpMethods.GET, s3.HttpMethods.HEAD, s3.HttpMethods.DELETE],
                allowed_origins=["*"],
                allowed_headers=["*"],
                max_age=3000
            )],
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # transcripts bucket TODO
        self.transcripts_bucket = s3.Bucket(
            self, "TranscriptsBucket",
            bucket_name=PhysicalName.GENERATE_IF_NEEDED,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.HEAD],
                allowed_origins=["*"],
                allowed_headers=["*"]
            )],
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
