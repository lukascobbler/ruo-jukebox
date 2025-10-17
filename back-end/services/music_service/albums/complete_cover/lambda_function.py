import os, json, boto3
dynamodb = boto3.resource("dynamodb")
ALBUMS = dynamodb.Table(os.environ["ALBUMS_TABLE"])

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
    album_id  = body.get("album_id")
    cover_key = body.get("cover_key")
    if not (album_id and cover_key):
        return _resp(400, {"message":"album_id and cover_key required"})
    ALBUMS.update_item(
        Key={"album_id": album_id},
        UpdateExpression="SET cover_key=:ck",
        ExpressionAttributeValues={":ck": cover_key}
    )
    return _resp(200, {"message":"cover set", "album_id": album_id, "cover_key": cover_key})

def _resp(code, body):
    return {"statusCode": code, "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body)}
