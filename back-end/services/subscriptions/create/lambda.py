from pre_authorize import pre_authorize
from create import create_subscription
import json
from general_utils import response

@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    user_id = event["userId"]
    body = json.loads(event.get("body", "{}"))
    target_id = body.get("targetId")
    result = create_subscription(user_id, target_id)
    return response(201, result)


