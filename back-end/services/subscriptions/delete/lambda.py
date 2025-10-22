from pre_authorize import pre_authorize
from delete import delete_subscription
import os, boto3, json
from general_utils import response

dynamodb = boto3.resource("dynamodb")
sub_table = dynamodb.Table(os.environ["USERDATA_TABLE"])


@pre_authorize(['Admin','LoggedInUser'])
def lambda_handler(event, context):
    user_id = event["userId"]

    body = json.loads(event.get("body", "{}"))
    target_id = body.get("id") or body.get("target_id")

    target_type, uuid = target_id.split("~", 1)

    delete_subscription(sub_table, user_id, target_type, uuid)

    return response(200, {"ok": True, "user_id": user_id, "topic": target_type, "id": uuid})