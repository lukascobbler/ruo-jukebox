from pre_authorize import pre_authorize
import json
from create import create_rating
from general_utils import response

@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    body = json.loads(event.get("body"))
    user_id = event["userId"]
    song_id = body.get("songId").strip()
    score = body.get("rating").strip()
    rating = create_rating(user_id,song_id,score) # try like this, if it fails, first read and then update or create
    return response(200, rating)