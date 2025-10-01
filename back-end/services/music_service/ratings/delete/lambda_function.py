import os, json, boto3
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

    r = R.get_item(Key={"track_id": track_id, "user_id": uid})
    item = r.get("Item")
    if not item:
        return _resp(404, {"message":"no rating"})
    R.delete_item(Key={"track_id": track_id, "user_id": uid})
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps({"type":"RATING_DEC","track_id":track_id,"rating":int(item["rating"])}))
    return _resp(204, "")
