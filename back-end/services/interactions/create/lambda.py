from pre_authorize import pre_authorize
from create import create_interaction
import json
from general_utils import response

@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    user_id = event["userId"]
    body = json.loads(event.get("body", "{}"))
    song_id = body.get('songId')
    artist_ids = body.get('artist_ids')
    genre_ids = body.get('genre_ids')
    album_id = body.get('album_id', None)
    value = body.get('value')
    result = create_interaction(user_id, song_id, artist_ids, genre_ids,value, album_id)
    return response(201, result)
