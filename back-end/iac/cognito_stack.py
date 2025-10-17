from constructs import Construct
from aws_cdk import (
    Stack, Duration, RemovalPolicy,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_cognito as cognito,
    aws_iam as iam, CfnOutput
)

LOGGED_IN_GROUP_NAME = "LoggedInUser"
ADMIN_GROUP_NAME = "Admin"

class CognitoStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.user_pool = None
        self.auth_kwargs = None

        self._define_user_pool()
        self._define_user_groups()
        self._add_pre_post_user_actions()
        self._define_auth_kwargs()
        self._expose_objects()

    def _define_user_pool(self):
        self.user_pool = cognito.UserPool(
            self, "JukeboxUserPool",
            self_sign_up_enabled=True, # users register themselves
            sign_in_aliases=cognito.SignInAliases(username=True, email=True), # use either username or email to sign in
            standard_attributes=cognito.StandardAttributes(
                # required attributes
                given_name=cognito.StandardAttribute(required=True, mutable=True),
                family_name=cognito.StandardAttribute(required=True, mutable=True),
                birthdate=cognito.StandardAttribute(required=True, mutable=True),
                email=cognito.StandardAttribute(required=True, mutable=True),
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.app_client = self.user_pool.add_client(
            "JukeBoxClient",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(user_password=True),
        )

    def _define_user_groups(self):
        # defines the user group
        cognito.CfnUserPoolGroup(
            self, "UsersGroup",
            group_name=LOGGED_IN_GROUP_NAME,
            user_pool_id=self.user_pool.user_pool_id
        )
        # defines the admin group
        cognito.CfnUserPoolGroup(
            self, "AdminsGroup",
            group_name=ADMIN_GROUP_NAME,
            user_pool_id=self.user_pool.user_pool_id
        )

    def _add_pre_post_user_actions(self):
        # lambda that auto-confirms email for cognito
        auto_confirm_mail = _lambda.Function(
            self, "CognitoPreSignUp",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="auto_confirm_mail.lambda_handler",
            code=_lambda.Code.from_asset("services/auth/auto_confirm_mail"),
            timeout=Duration.seconds(5),
            memory_size=128,
        )

        # apply the auto email confirm lambda before the user is created
        self.user_pool.add_trigger(cognito.UserPoolOperation.PRE_SIGN_UP, auto_confirm_mail)

        # lambda that adds user to the logged-in user group
        add_user_to_user_group = _lambda.Function(
            self, "CognitoPostConfirm",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="add_user_to_user_group.lambda_handler",
            code=_lambda.Code.from_asset("services/auth/add_user_to_user_group"),
            environment={
                "GROUP_NAME": "LoggedInUser",
            },
            timeout=Duration.seconds(10),
            memory_size=256,
        )

        # apply the add user to group lambda after the user is created
        self.user_pool.add_trigger(cognito.UserPoolOperation.POST_CONFIRMATION, add_user_to_user_group)

        # gives permission to the lambda that adds a user to a group to add users to groups (the resource)
        add_user_to_user_group.add_to_role_policy(iam.PolicyStatement(
            actions=["cognito-idp:AdminAddUserToGroup"],
            resources=[f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{self.user_pool.user_pool_id}"]
        ))

    def _define_auth_kwargs(self):
        # only the users from our user pool can log in
        authorizer = apigw.CognitoUserPoolsAuthorizer(self, "ApiAuthorizer", cognito_user_pools=[self.user_pool])
        # predefined kwargs to put on every API gateway route
        self.auth_kwargs = dict(authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO)

    def _expose_objects(self):
        CfnOutput(self, "UserPoolId", value=self.user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=self.app_client.user_pool_client_id)