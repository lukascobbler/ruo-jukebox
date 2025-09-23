from aws_cdk import App
from iac.backend_stack import BackendStack
from iac.database_stack import DatabaseStack

app = App()

db_stack = DatabaseStack(app, "DemoDatabaseStack",
                         env={'region': 'eu-central-1'})

backend_stack = BackendStack(app, "DemoBackendStack",
                             table=db_stack.table,
                             env={'region': 'eu-central-1'})

app.synth()
