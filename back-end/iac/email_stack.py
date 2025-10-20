from aws_cdk import Stack, aws_iam as iam
from constructs import Construct


class EmailStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.send_policy = iam.ManagedPolicy(
            self, "SesSendPolicy",
            managed_policy_name="AllowSesSendEmail",
            statements=[
                iam.PolicyStatement(
                    actions=["ses:SendEmail", "ses:SendRawEmail"],
                    resources=["*"]
                )
            ]
        )
