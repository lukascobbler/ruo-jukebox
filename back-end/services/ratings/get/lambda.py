from pre_authorize import pre_authorize
import json
from read import get_rating
from general_utils import response

@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    user_id = event["userId"]
    path_params = event.get("pathParameters")
    song_id = path_params.get("songId").strip()
    
    rating = get_rating(user_id,song_id)
    return response(200, rating)