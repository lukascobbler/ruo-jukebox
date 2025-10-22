from pre_authorize import pre_authorize
from delete import delete_subscription
import json
from general_utils import response

@pre_authorize(['Admin','User'])
def lambda_handler(event, context):
    user_id = event["userId"]
    path_params = event.get("pathParameters")
    target_id = path_params.get("topic")


    delete_subscription(user_id, target_id)

    return response(200, target_id)
