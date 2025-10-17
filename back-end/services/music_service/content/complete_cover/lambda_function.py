import os, json, boto3
dynamodb = boto3.resource("dynamodb")
TRACKS = dynamodb.Table(os.environ["TRACKS_TABLE"])
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
    cover_key = body.get("cover_key")
    if not (track_id and cover_key):
        return _resp(400, {"message":"track_id and cover_key required"})
    TRACKS.update_item(
        Key={"track_id": track_id},
        UpdateExpression="SET cover_key=:ck",
        ExpressionAttributeValues={":ck": cover_key}
    )
    return _resp(200, {"message":"cover set", "track_id": track_id, "cover_key": cover_key})

def _resp(code, body):
    return {"statusCode": code, "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body)}
