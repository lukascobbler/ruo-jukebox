from pre_authorize import pre_authorize
from create import create_subscription
import os, boto3

dynamodb = boto3.resource("dynamodb")
sub_table = dynamodb.Table(os.environ["USERDATA_TABLE"])


@pre_authorize(['Admin', 'LoggedInUser'])
def lambda_handler(event, context):
    user_id = event["userId"]
    body = request(event).json or {}
    target_id = body.get("id") or body.get("target_id")
    target_type, uuid = target_id.split("~", 1)
    result = create_subscription(user_id, target_type, uuid)
    return _resp(201, {"ok": True, "user_id": user_id, "topic": target_type, "id": uuid})