from aws_cdk.aws_cognito import UserPoolGroup, AuthFlow, SignInAliases, StandardAttribute, UserPool, StandardAttributes, PasswordPolicy, StringAttribute
from aws_cdk import NestedStack, RemovalPolicy, Duration
from constructs import Construct

ADMIN_GROUP_NAME = "Admin"
USER_GROUP_NAME = "User"


class CognitoStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)

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
            custom_attributes={"userId": StringAttribute(mutable=True)},
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

        UserPoolGroup(self, "UserGroup", user_pool=self.user_pool, group_name=USER_GROUP_NAME)
        UserPoolGroup(self, "AdminGroup", user_pool=self.user_pool, group_name=ADMIN_GROUP_NAME)
