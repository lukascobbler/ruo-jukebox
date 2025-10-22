from aws_cdk import NestedStack, aws_apigateway as apigw
from aws_cdk import aws_certificatemanager as acm
from aws_cdk.aws_cognito import UserPool
from constructs import Construct


class ApiGatewayStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, branch: str, user_pool: UserPool, **kwargs):
        super().__init__(scope, stack_id, **kwargs)

        api_domain = f"{branch}.api.jb.moma.rs" if branch != "main" else "api.jb.moma.rs"

        self.api = apigw.RestApi(
            self, "ApiGateway",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                allow_headers=apigw.Cors.DEFAULT_HEADERS,
                allow_origins=apigw.Cors.ALL_ORIGINS
            ),
            endpoint_configuration=apigw.EndpointConfiguration(types=[apigw.EndpointType.REGIONAL]),
        )

        certificate = acm.Certificate.from_certificate_arn(
            self, "ApiCert",
            "arn:aws:acm:eu-central-1:172132042466:certificate/9e6fa06e-5acc-464c-9d06-5667e13e28b5"
        )

        self.domain_name = apigw.DomainName(
            self, "CustomDomain",
            domain_name=api_domain,
            certificate=certificate,
            endpoint_type=apigw.EndpointType.REGIONAL
        )

        apigw.BasePathMapping(
            self, "ApiMapping",
            domain_name=self.domain_name,
            rest_api=self.api,
            base_path="",
            stage=self.api.deployment_stage
        )

        self.authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "ApiAuthorizer",
            cognito_user_pools=[user_pool],
        )

        self.auth_kwargs = dict(
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO
        )
