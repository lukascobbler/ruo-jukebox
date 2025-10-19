from aws_cdk.aws_cognito import UserPoolGroup, AuthFlow, SignInAliases, StandardAttribute, UserPool, StandardAttributes, PasswordPolicy
from aws_cdk import Stack, RemovalPolicy, CfnOutput, Duration
from constructs import Construct

LOGGED_IN_GROUP_NAME = "LoggedInUser"
ADMIN_GROUP_NAME = "Admin"

class CognitoStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.user_pool: UserPool = None
        self.app_client = None

        self._define_user_pool()
        self._define_user_groups()
        self._expose_objects()

    def _define_user_pool(self):
        self.user_pool = UserPool(
            self, "JukeboxUserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=SignInAliases(username=True, email=True),
            standard_attributes=StandardAttributes(
                given_name=StandardAttribute(required=True, mutable=True),
                family_name=StandardAttribute(required=True, mutable=True),
                birthdate=StandardAttribute(required=True, mutable=True),
                email=StandardAttribute(required=True, mutable=True),
            ),
            password_policy=PasswordPolicy(
                min_length=6,
                require_uppercase=False,
                require_lowercase=False,
                require_digits=False,
                require_symbols=False
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.app_client = self.user_pool.add_client(
            "JukeBoxClient",
            generate_secret=False,
            auth_flows=AuthFlow(user_password=True),
            access_token_validity=Duration.hours(24),
            id_token_validity=Duration.hours(24),
        )

    def _define_user_groups(self):
        UserPoolGroup(self, "LoggedInUsersGroup", user_pool=self.user_pool, group_name=LOGGED_IN_GROUP_NAME)
        UserPoolGroup(self, "AdminGroup", user_pool=self.user_pool, group_name=ADMIN_GROUP_NAME)

    def _expose_objects(self):
        CfnOutput(self, "UserPoolId", value=self.user_pool.user_pool_id, export_name="CognitoUserPoolId")
        CfnOutput(self, "UserPoolClientId", value=self.app_client.user_pool_client_id, export_name="CognitoUserPoolClientId")
