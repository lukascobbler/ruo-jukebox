## Backend setup

1. Create venv and activate:
   - Linux: `python -m venv .venv && source .venv/bin/activate`
   - Windows: `python -m venv .venv; .\.venv\Scripts\Activate.ps1`
2. Install dependencies: \
   `pip install -r requirements.txt`
3. Install AWS CDK: \
   `npm install -g aws-cdk`
4. Bootstrap (run once per account/region): \
   `cdk bootstrap aws://<ACCOUNT_ID>/eu-central-1`

## Backend deployment

1. Deploy stack: \
   `cdk deploy DatabaseStack --require-approval never` \
   `cdk deploy BackendStack --require-approval never`
2. Destroy (if needed): \
   `cdk destroy DatabaseStack --force` \
   `cdk destroy BackendStack --force`
