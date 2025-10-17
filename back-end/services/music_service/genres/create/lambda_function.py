import os, json, time, re, boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
GENRES = dynamodb.Table(os.environ["GENRES_TABLE"])
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

def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def _json_default(o):
    if isinstance(o, Decimal):
        return int(o) if o % 1 == 0 else float(o)
    raise TypeError

def _resp(code, body):
    return {"statusCode": code,
            "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}

def lambda_handler(event, context):
    guard = _require_admin(event)
    if guard: 
        return guard
    body = json.loads(event.get("body") or "{}")
    name = (body.get("name") or "").strip()
    description = body.get("description") or ""

    if not name:
        return _resp(400, {"message":"name is required"})

    genre_id = slugify(name)

    # Idempotent create: if already exists, just return it
    r = GENRES.get_item(Key={"genre_id": genre_id})
    if "Item" in r:
        return _resp(200, r["Item"])

    item = {
        "genre_id": genre_id,
        "name": name,
        "description": description,
        "created_at": int(time.time()*1000)
    }
    GENRES.put_item(Item=item)
    return _resp(201, item)
