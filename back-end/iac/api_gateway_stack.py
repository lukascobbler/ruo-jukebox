from constructs import Construct
from aws_cdk import (
    Stack, Duration, RemovalPolicy,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_events,
    aws_apigateway as apigw,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_certificatemanager as acm
)


class ApiGatewayStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.api = None

    def _define_api(self):
        self.api = apigw.RestApi(
            self, "ApiGateway",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS(),  # TODO change
                allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                allow_headers=apigw.Cors.DEFAULT_HEADERS()
            ),
            endpoint_configuration=apigw.EndpointConfiguration(types=[apigw.EndpointType.REGIONAL]),
        )

        # Settings for custom domain
        certificate = acm.Certificate.from_certificate_arn(
            self, "ApiCert",
            "arn:aws:acm:eu-central-1:172132042466:certificate/779aabb6-2c06-4075-b2a4-31fac8a4cb2c"
        )

        domain_name = apigw.DomainName(
            self, "CustomDomain",
            domain_name="api.jb.moma.rs",
            certificate=certificate,
        )

        apigw.BasePathMapping(
            self, "ApiMapping",
            domain_name=domain_name,
            rest_api=self.api,
            base_path="",
            stage=self.api.deployment_stage
        )