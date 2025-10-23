from aws_cdk import (
    Duration,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_lambda_event_sources as events, PhysicalName,
    NestedStack
)
from aws_cdk.aws_lambda import DockerImageFunction, DockerImageCode, Function, Code, Runtime
from aws_cdk.aws_s3_notifications import LambdaDestination
from constructs import Construct


class TranscriptionStack(NestedStack):
    def __init__(self, scope: Construct, id: str, s3_stack, environment: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        audio_bucket = s3_stack.audio_bucket
        transcripts_bucket = s3_stack.transcripts_bucket

        transcription_dlq = sqs.Queue(
            self, "TranscriptionDLQ",
            retention_period=Duration.days(14)
        )

        transcription_queue = sqs.Queue(
            self, "TranscriptionQueue",
            queue_name=PhysicalName.GENERATE_IF_NEEDED,
            visibility_timeout=Duration.minutes(15),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=5,
                queue=transcription_dlq
            )
        )

        self.consumer_lambda = DockerImageFunction(
            self, "TranscriptionConsumerLambda",
            code=DockerImageCode.from_image_asset("services/transcription/transcribe"),
            memory_size=2048,
            timeout=Duration.minutes(10),
            environment={
                "MODEL_TYPE": "small",
                **environment
            },
        )

        audio_bucket.grant_read(self.consumer_lambda)
        transcripts_bucket.grant_read_write(self.consumer_lambda)

        self.consumer_lambda.add_event_source(
            events.SqsEventSource(transcription_queue, batch_size=5)
        )

        self.producer_lambda = Function(
            self,
            "TranscriptionProducerLambda",
            handler="lambda.lambda_handler",
            code=Code.from_asset("services/transcription/start_transcription"),
            environment={
                "QUEUE_URL": transcription_queue.queue_url,
                **environment
            },
            timeout=Duration.seconds(30),
            runtime=Runtime.PYTHON_3_12,
        )

        audio_bucket.grant_read(self.producer_lambda)
        transcription_queue.grant_send_messages(self.producer_lambda)

        audio_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            LambdaDestination(self.producer_lambda),
            s3.NotificationKeyFilter(prefix="songs/", suffix=".mp3")
        )
