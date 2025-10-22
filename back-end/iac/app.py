from aws_cdk import App, Environment
from iac.root_stack import RootStack
import os

app = App()

env = Environment(account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION"))
branch = app.node.try_get_context("branch") or "main"
suffix = f"-{branch}" if branch != "main" else ""

RootStack(app, f"RootStack{suffix}", branch=branch, env=env)

app.synth()
