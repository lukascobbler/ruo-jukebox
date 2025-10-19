from aws_cdk.aws_cognito import UserPoolGroup, AuthFlow, SignInAliases, StandardAttribute, UserPool, UserPoolOperation, StandardAttributes
from aws_cdk import Stack, Duration, RemovalPolicy, aws_lambda as _lambda, CfnOutput
from iac.constructs.lambda_with_permissions import LambdaWithPermissions
from aws_cdk.aws_iam import ManagedPolicy, PolicyStatement
from iac.shared_layer_stack import SharedLayerStack
from iac.dynamo_db_stack import DynamoDbStack
from aws_cdk import aws_apigateway as apigw
from iac.s3_stack import S3Stack
from constructs import Construct

LOGGED_IN_GROUP_NAME = "LoggedInUser"
ADMIN_GROUP_NAME = "Admin"


class CognitoStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.user_pool: UserPool = None
        self.app_clientapp_client = None
        self.lambdas = {}

        self._define_user_pool()
        self._define_user_groups()
        self._add_pre_post_user_actions()
        self._expose_objects()

    def _define_user_pool(self):
        self.user_pool = UserPool(
            self, "JukeboxUserPool",
            self_sign_up_enabled=True,  # users register themselves
            sign_in_aliases=SignInAliases(username=True, email=True),  # use either username or email to sign in
            standard_attributes=StandardAttributes(
                # required attributes
                given_name=StandardAttribute(required=True, mutable=True),
                family_name=StandardAttribute(required=True, mutable=True),
                birthdate=StandardAttribute(required=True, mutable=True),
                email=StandardAttribute(required=True, mutable=True),
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.app_client = self.user_pool.add_client(
            "JukeBoxClient",
            generate_secret=False,
            auth_flows=AuthFlow(user_password=True),
        )

    def _define_user_groups(self):
        # defines the user group
        UserPoolGroup(
            self,
            "LoggedInUsersGroup",
            user_pool=self.user_pool,
            group_name=LOGGED_IN_GROUP_NAME,
        )
        # defines the admin group
        UserPoolGroup(
            self,
            "AdminGroup",
            user_pool=self.user_pool,
            group_name=ADMIN_GROUP_NAME,
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
        self.user_pool.add_trigger(UserPoolOperation.PRE_SIGN_UP, auto_confirm_mail)

        # lambda that adds user to the logged-in user group
        add_user_to_user_group = _lambda.Function(
            self, "CognitoPostConfirm",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="add_user_to_user_group.lambda_handler",
            code=_lambda.Code.from_asset("services/auth/add_user_to_user_group"),
            environment={
                "GROUP_NAME": LOGGED_IN_GROUP_NAME,
            },
            timeout=Duration.seconds(10),
            memory_size=256,
        )

        # apply the add user to group lambda after the user is created
        self.user_pool.add_trigger(
            UserPoolOperation.POST_CONFIRMATION,
            add_user_to_user_group
        )

        # gives permission to the lambda that adds a user to a group to add users to groups (the resource)
        add_user_to_user_group.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("AmazonCognitoPowerUser")
        )

    def _expose_objects(self):
        CfnOutput(self, "UserPoolId", value=self.user_pool.user_pool_id, export_name="CognitoUserPoolId")
        CfnOutput(self, "UserPoolClientId", value=self.app_client.user_pool_client_id, export_name="CognitoUserPoolClientId")

    def create_lambdas(self, dynamo_db: DynamoDbStack, s3: S3Stack, shared_layer_stack: SharedLayerStack, env):
        lambda_defs = {
            "HelloTest": "services/auth/hello_test",
            "Register": "services/auth/register",
            "Login": "services/auth/login",
            "Logout": "services/auth/logout"
        }
        for key, path in lambda_defs.items():
            self.lambdas[key] = LambdaWithPermissions(self, key, path, env, dynamo_db, s3, shared_layer_stack).fn

        # Register lambda needs additional Cognito permissions
        self.lambdas["Register"].add_to_role_policy(
            PolicyStatement(
                actions=[
                    "cognito-idp:AdminCreateUser",
                    "cognito-idp:AdminConfirmSignUp",
                    "cognito-idp:AdminAddUserToGroup"
                ],
                resources=[self.user_pool.user_pool_arn]
            )
        )

    def attach_to_api(self, api: apigw.RestApi):
        auth = api.root.add_resource("auth")
        auth.add_resource("register").add_method("POST", apigw.LambdaIntegration(self.lambdas["Register"]), authorizer=None)
        auth.add_resource("login").add_method("POST", apigw.LambdaIntegration(self.lambdas["Login"]), authorizer=None)
        auth.add_resource("logout").add_method("POST", apigw.LambdaIntegration(self.lambdas["Logout"]))
        auth.add_resource("hello_test").add_method("GET", apigw.LambdaIntegration(self.lambdas["HelloTest"]))
