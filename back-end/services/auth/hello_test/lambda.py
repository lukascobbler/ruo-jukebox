import passlib.hash
def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": f"Hello! {passlib.hash.pbkdf2_sha256.hash('test')}"
    }