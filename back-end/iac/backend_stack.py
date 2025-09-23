from iac.constructs.lambda_with_sqs import LambdaWithSqs
from constructs import Construct
from aws_cdk import (Stack,
                     Duration,
                     aws_sqs as sqs,
                     aws_lambda as _lambda,
                     aws_apigateway as apigw,
                     aws_certificatemanager as acm)


class BackendStack(Stack):
    def __init__(self, scope: Construct, id: str, table, **kwargs):
        super().__init__(scope, id, **kwargs)

        # SQS Queue
        queue = sqs.Queue(
            self, "DemoQueue",
            visibility_timeout=Duration.seconds(30),
            retention_period=Duration.days(1)
        )

        # Lambda Functions
        add_lambda = _lambda.Function(
            self, "AddLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("services/demo_service/add_endpoint"),
            environment={"QUEUE_URL": queue.queue_url}
        )

        # može i ovako, ne mora se koristiti construct ako je nešto jednostavno
        # processor_lambda = _lambda.Function(
        #     self, "ProcessorLambda",
        #     runtime=_lambda.Runtime.PYTHON_3_11,
        #     handler="lambda_function.lambda_handler",
        #     code=_lambda.Code.from_asset("lambdas/processor"),
        #     environment={"TABLE_NAME": table.table_name}
        # )

        processor_lambda = LambdaWithSqs(self, "ProcessorLambda", queue=queue,
                                         handler_path="services/demo_service/processor",
                                         env={"TABLE_NAME": table.table_name})

        read_lambda = _lambda.Function(
            self, "ReadLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("services/demo_service/read_endpoint"),
            environment={"TABLE_NAME": table.table_name}
        )

        # Permissions
        table.grant_read_write_data(processor_lambda.lambda_function)
        table.grant_read_data(read_lambda)
        queue.grant_send_messages(add_lambda)
        queue.grant_consume_messages(processor_lambda.lambda_function)

        # not needed because we have made special construct to be reused
        # SQS Trigger
        # processor_lambda.add_event_source(lambda_event_sources.SqsEventSource(queue))

        # API Gateway
        api = apigw.RestApi(self, "DemoApi")
        api.root.add_resource("add").add_method("POST", apigw.LambdaIntegration(add_lambda))
        api.root.add_resource("read").add_method("GET", apigw.LambdaIntegration(read_lambda))

        # Settings for custom domain
        certificate = acm.Certificate.from_certificate_arn(
            self, "ApiCert",
            "arn:aws:acm:eu-central-1:779156816822:certificate/875c9c89-5b45-4b0e-8074-80685d61308a"
        )

        domain_name = apigw.DomainName(
            self, "CustomDomain",
            domain_name="api.jukebox.moma.rs",
            certificate=certificate,
        )

        apigw.BasePathMapping(
            self, "ApiMapping",
            domain_name=domain_name,
            rest_api=api,
            base_path="",
            stage=api.deployment_stage
        )
