from aws_cdk import Duration, aws_sqs as sqs, aws_lambda_event_sources as events, PhysicalName, NestedStack
from aws_cdk.aws_lambda import DockerImageFunction, DockerImageCode, Function, Code, Runtime
from iac.shared.s3_stack import S3Stack
from constructs import Construct


class TranscriptionStack(NestedStack):
    def __init__(self, scope: Construct, id: str, s3_stack: S3Stack, environment: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

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

        s3_stack.audio_bucket.grant_read(self.consumer_lambda)
        s3_stack.transcripts_bucket.grant_read_write(self.consumer_lambda)

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

        s3_stack.audio_bucket.grant_read(self.producer_lambda)
        transcription_queue.grant_send_messages(self.producer_lambda)
