from general_utils import response, file_exists_on_s3, get_genre_objects
from pre_authorize import pre_authorize
from create import create_artist
from read import get_contents
import json


@pre_authorize(['Admin'])
def lambda_handler(event, context):
    body = json.loads(event.get("body"))

    artist_id = body.get("artist_id").strip()
    name = body.get("name").strip()
    biography = body.get("biography").strip()
    genres = body.get("genres")

    if not isinstance(artist_id, str) or not artist_id.startswith("ARTIST~"):
        return response(400, error="Field 'artist_id' must start with 'ARTIST~'")

    if not artist_id: return response(400, error="Field 'artist_id' is required")
    if not name: return response(400, error="Field 'name' is required")
    if not biography: return response(400, error="Field 'biography' is required")

    genres, message = get_genre_objects(genres)
    if not genres: return response(400, error=message)

    core_artist = create_artist(artist_id, name, biography, genres)

    return response(200, core_artist)
