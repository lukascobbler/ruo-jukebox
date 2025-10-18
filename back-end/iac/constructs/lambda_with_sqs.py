from aws_cdk import aws_lambda as _lambda, aws_sqs as sqs, aws_lambda_event_sources as lambda_event_sources
from constructs import Construct

# Ima smisla definisati Constructe ako su kompleksniji i koriste se više puta, inače može sve odmah u stack


class LambdaWithSqs(Construct):
    def __init__(self, scope: Construct, id_str: str, queue: sqs.IQueue, handler_path: str, env: dict):
        super().__init__(scope, id_str)
        self.lambda_function = _lambda.Function(
            self, "Lambda",
            runtime=_lambda.Runtime.PYTHON_3_11(),
            handler="lambda.lambda_handler",
            code=_lambda.Code.from_asset(handler_path),
            environment=env
        )

        # Add SQS trigger automatically
        self.lambda_function.add_event_source(lambda_event_sources.SqsEventSource(queue))
