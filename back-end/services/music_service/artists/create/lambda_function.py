import os, json, time, uuid, boto3
dynamodb = boto3.resource("dynamodb")
ARTISTS = dynamodb.Table(os.environ["ARTISTS_TABLE"])
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
    name = (body.get("name") or "").strip()
    bio = body.get("bio") or ""
    genres = body.get("genres") or []
    if not name:
        return _resp(400, {"message": "name is required"})
    now = int(time.time()*1000)
    item = {"artist_id": str(uuid.uuid4()), "name": name, "bio": bio, "genres": genres,
            "created_at": now, "updated_at": now}
    ARTISTS.put_item(Item=item)
    return _resp(201, item)

def _resp(code, body):
    return {"statusCode": code, "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body)}
