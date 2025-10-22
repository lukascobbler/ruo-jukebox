from pre_authorize import pre_authorize
import json
from delete import delete_rating
from general_utils import response

@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    body = json.loads(event.get("body"))
    user_id = event["userId"]
    song_id = body.get("songId").strip()
    delete_rating(user_id,song_id)
    return response(200, {})