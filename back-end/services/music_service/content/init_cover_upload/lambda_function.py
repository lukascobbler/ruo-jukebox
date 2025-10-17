import os, json, boto3
s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]
def _claims(event):
    return (event.get("requestContext") or {}).get("authorizer", {}).get("claims", {}) or {}

def _require_admin(event):
    claims = _claims(event)
    groups = (claims.get("cognito:groups") or "")
    if "admin" not in groups.split(","):
        return {
            "statusCode": 403,
            "headers": {"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps({"message":"admin only"})
        }

def lambda_handler(event, context):
    guard = _require_admin(event)
    if guard: 
        return guard
    body = json.loads(event.get("body") or "{}")
    track_id  = body.get("track_id")
    file_name = (body.get("file_name") or "").strip()
    file_type = (body.get("file_type") or "").strip()
    if not (track_id and file_name and file_type):
        return _resp(400, {"message":"track_id, file_name, file_type required"})
    key = f"covers/tracks/{track_id}/{file_name}"
    url = s3.generate_presigned_url("put_object",
            Params={"Bucket": BUCKET, "Key": key, "ContentType": file_type}, ExpiresIn=600)
    return _resp(200, {"track_id": track_id, "cover_key": key, "upload_url": url})

def _resp(code, body):
    return {"statusCode": code, "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body)}
