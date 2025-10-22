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

1. Add requirements to libs layer: \
   `pip install -r requirements.txt -t libs_layer/python`
2. Deploy stack: \
   `cdk deploy CognitoStack --require-approval never` \
   `cdk deploy --all --require-approval never`
3. Destroy (if needed): \
   `cdk destroy CognitoStack --force` 
