import os, json, boto3, time
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")
R = dynamodb.Table(os.environ["RATINGS_TABLE"])
QUEUE_URL = os.environ["QUEUE_URL"]

def _json_default(o):
    if isinstance(o, Decimal): return int(o) if o % 1 == 0 else float(o)
    raise TypeError
def _resp(code, body):
    return {"statusCode": code, "headers":{"Content-Type":"application/json","Access-Control-Allow-Origin":"*"},
            "body": json.dumps(body, default=_json_default)}
def _uid(event):
    claims = (event.get("requestContext") or {}).get("authorizer", {}).get("claims", {})
    return claims.get("sub")

def lambda_handler(event, context):
    uid = _uid(event)
    if not uid: return _resp(401, {"message":"unauthorized"})
    track_id = event["pathParameters"]["id"]
    body = json.loads(event.get("body") or "{}")
    new_rating = int(body.get("rating", 0))
    if new_rating not in (1,2,3):
        return _resp(400, {"message":"rating must be 1..3"})

    # read old rating if exists
    old = R.get_item(Key={"track_id": track_id, "user_id": uid}).get("Item")
    R.put_item(Item={"track_id": track_id, "user_id": uid, "rating": new_rating, "ts": int(time.time()*1000)})

    # enqueue delta messages
    if old and old.get("rating") != new_rating:
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps({"type":"RATING_DEC","track_id":track_id,"rating":int(old["rating"])}))
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps({"type":"RATING_INC","track_id":track_id,"rating":new_rating}))
    elif not old:
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps({"type":"RATING_INC","track_id":track_id,"rating":new_rating}))

    return _resp(200, {"message":"ok", "track_id": track_id, "rating": new_rating})
