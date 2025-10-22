from pre_authorize import pre_authorize
from read import get_subscriptions_for_user
from general_utils import response

@pre_authorize(['Admin','User'])
def lambda_handler(event, context):
    user_id = event["userId"]
    subs = get_subscriptions_for_user(user_id)
    return response(200, subs)