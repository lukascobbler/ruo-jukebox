from general_utils import response, file_exists_on_s3, get_genre_objects, get_artists_objects
from create import create_album, get_contents
import json, os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]


def lambda_handler(event, context):
    body = json.loads(event.get("body"))

    album_id = body.get("album_id").strip()
    song_ids = body.get("song_ids")
    name = body.get("name").strip()
    artists = body.get("artists")
    genres = body.get("genres")

    artists, message = get_artists_objects(artists)
    if not artists: return response(400, error=message)

    genres, message = get_genre_objects(genres)
    if not genres: return response(400, error=message)

    # todo batch kreirati pesme nakon kreiranja albuma, nisam prosledjivao nikakve detalje u vezi samih pesama koje ce trebati da se azuriraju
    #  pa je to malo zajebano, pogledati detaljnije

    core_album = create_album(album_id, name, artists, genres)

    return response(200, core_album)
