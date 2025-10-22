from aws_cdk import NestedStack, aws_iam as iam
from constructs import Construct


class EmailStack(NestedStack):
    def __init__(self, scope: Construct, stack_id: str, branch: str, **kwargs):
        super().__init__(scope, stack_id, **kwargs)

        suffix = f"-{branch}" if branch != "main" else ""

        self.send_policy = iam.ManagedPolicy(
            self, "SesSendPolicy",
            managed_policy_name=f"AllowSesSendEmail{suffix}",
            statements=[
                iam.PolicyStatement(
                    actions=["ses:SendEmail", "ses:SendRawEmail"],
                    resources=["*"]
                )
            ]
        )
