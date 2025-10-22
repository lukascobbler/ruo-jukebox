from general_utilities import generate_s3_download_url, response
from pre_authorize import pre_authorize
from read import songs_for_album
import json

@pre_authorize(['Admin', 'User'])
def lambda_handler(event, context):
    body = json.loads(event.get('body'))
    album_id = body.get('album_id').strip()

    all_songs_for_album = songs_for_album(album_id)
    for song in all_songs_for_album:
        song['audio_url'] = generate_s3_download_url(song['audio_key'])

    return response(200, all_songs_for_album)
