from general_utils import response, file_exists_on_s3, get_genre_objects, get_artist_objects
from create import create_single, create_songs
from pre_authorize import pre_authorize
from read import get_contents
import json, os

AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]


@pre_authorize(['Admin'])
def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    single_id = body.get("single_id").strip()
    song_id = body.get("song_id").strip()
    name = body.get("name").strip()
    artists = body.get("artists")
    genres = body.get("genres")

    if not single_id: return response(400, error="Field 'single_id' is required")
    if not song_id: return response(400, error="Field 'song_id' is required")
    if not name: return response(400, error="Field 'name' is required")

    audio_key = f"songs/{song_id}.mp3"
    if not file_exists_on_s3(AUDIO_BUCKET, audio_key):
        return response(400, error="Song audio not found")

    cover_key = f"singles/{single_id}.jpg"
    if not file_exists_on_s3(IMAGES_BUCKET, cover_key):
        cover_key = ""

    genres, message = get_genre_objects(genres)
    if genres is None: return response(400, error=message)

    artists, message = get_artist_objects(artists)
    if artists is None: return response(400, error=message)

    core_song = {
        "content_id": song_id,
        "content_type": "SONG",
        "name": name,
        "name_lc": name.lower(),
        "audio_key": audio_key,
        "cover_key": cover_key,
        "artists": artists,
        "genres": genres
    }

    core_single = create_single(single_id, name, artists, genres)
    create_songs(single_id, [core_song])

    return response(200, core_single)
