from general_utils import response, file_exists_on_s3, get_genre_objects, file_exists_on_s3
from pre_authorize import pre_authorize
from create import create_artist
from read import get_contents
import json, os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]


@pre_authorize(['Admin'])
def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    artist_id = body.get("artist_id").strip()
    biography = body.get("biography").strip()
    name = body.get("name").strip()
    genres = body.get("genres")

    if not isinstance(artist_id, str) or not artist_id.startswith("ARTIST~"):
        return response(400, error="Field 'artist_id' must start with 'ARTIST~'")

    if not name: return response(400, error="Field 'name' is required")

    genres, message = get_genre_objects(genres)
    if genres is None: return response(400, error=message)

    cover_key = f"artists/{artist_id}.jpg"
    if not file_exists_on_s3(IMAGES_BUCKET, cover_key):
        cover_key = None

    core_artist = create_artist(artist_id, name, biography, genres, cover_key)

    return response(200, core_artist)
