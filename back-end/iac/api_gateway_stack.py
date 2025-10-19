from aws_cdk import Stack, CfnOutput, aws_apigateway as apigw
from aws_cdk import aws_certificatemanager as acm
from aws_cdk.aws_cognito import UserPool
from constructs import Construct


class ApiGatewayStack(Stack):
    def __init__(self, scope: Construct, id: str, user_pool: UserPool, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.api = None
        self.auth_kwargs = None
        self.authorizer = None

        self._define_api()
        self._define_auth(user_pool)

    def _define_api(self):
        self.api = apigw.RestApi(
            self, "ApiGateway",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,  # TODO change
                allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                allow_headers=apigw.Cors.DEFAULT_HEADERS
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

        CfnOutput(self, "ApiId", value=self.api.rest_api_id)

    def _define_auth(self, user_pool: UserPool):
        # only the users from our user pool can log in
        self.authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "ApiAuthorizer",
            cognito_user_pools=[user_pool],
        )
        self.auth_kwargs = dict(
            authorizer=self.authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO
        )
