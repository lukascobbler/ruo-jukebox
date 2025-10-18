from aws_cdk.aws_iam import PolicyStatement
from constructs import Construct
from aws_cdk import (
    Stack, Duration, RemovalPolicy,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_events,
    aws_apigateway as apigw,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_certificatemanager as acm, CfnOutput
)

from iac.cognito_stack import CognitoStack
from iac.common import mk_lambda
from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack


class ApiGatewayStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 cognito: CognitoStack,
                 dynamo_db: DynamoDbStack, s3: S3Stack,
                 env,
                 **kwargs
                 ):
        super().__init__(scope, id, **kwargs)

        self.api = None
        self.auth_kwargs = None

        self._define_api()
        self._define_auth_kwargs(cognito)
        self._define_auth_api(cognito, dynamo_db, s3, env)

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

    def _define_auth_kwargs(self, cognito):
        # only the users from our user pool can log in
        authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "ApiAuthorizer",
            cognito_user_pools=[cognito.user_pool],
        )
        # predefined kwargs to put on every API gateway route
        self.auth_kwargs = dict(
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO
        )

    def _define_auth_api(self, cognito, dynamo_db, s3, env):
        hello_test_get = mk_lambda(self, "HelloTest", "services/auth/hello_test", env, dynamo_db, s3)
        register_submit = mk_lambda(self, "Register", "services/auth/register", env, dynamo_db, s3)
        login_submit = mk_lambda(self, "Login", "services/auth/login", env, dynamo_db, s3)
        logout_submit = mk_lambda(self, "Logout", "services/auth/logout", env, dynamo_db, s3)

        register_submit.add_to_role_policy(
            PolicyStatement(
                actions=[
                    "cognito-idp:AdminCreateUser",
                    "cognito-idp:AdminConfirmSignUp",
                    "cognito-idp:AdminAddUserToGroup"
                ],
                resources=[cognito.user_pool.user_pool_arn]
            )
        )

        auth = self.api.root.add_resource("auth")
        register = auth.add_resource("register")
        login = auth.add_resource("login")
        logout = auth.add_resource("logout")
        hello_test = auth.add_resource("hello_test")

        register.add_method(
            "POST",
            apigw.LambdaIntegration(register_submit),
            authorizer=None
        )
        login.add_method(
            "POST",
            apigw.LambdaIntegration(login_submit),
            authorizer=None
        )
        logout.add_method(
            "POST",
            apigw.LambdaIntegration(logout_submit)
        )
        hello_test.add_method(
            "GET",
            apigw.LambdaIntegration(hello_test_get)
        )

        CfnOutput(self, "ApiId", value=self.api.rest_api_id)