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
   `cdk deploy BackendStack --require-approval never`
2. Destroy (if needed): \
   `cdk destroy BackendStack --force`

## Fronted deployment
1. Build angular app: \
   `ng build --configuration production`
2. Upload to S3 storage: \
   `aws s3 sync dist/front-end/browser/ s3://jukebox-frontend/ --delete`
3. Invalidate CloudFront old cash: \
   `aws cloudfront create-invalidation --distribution-id E1IC7OO1GXB8I4 --paths "/*"`