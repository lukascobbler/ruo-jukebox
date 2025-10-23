from general_utils import response, file_exists_on_s3, get_genre_objects, get_artist_objects
from create import create_album, create_songs
import json, os

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    album_id = body.get("album_id")
    name = body.get("name")

    artists = body.get("artists")
    genres = body.get("genres")

    if not album_id: return response(400, error="Field 'album_id' is required")
    if not name: return response(400, error="Field 'name' is required")

    artists, message = get_artist_objects(artists)
    if not artists: return response(400, error=message)

    genres, message = get_genre_objects(genres)
    if genres is None: return response(400, error=message)

    cover_key = f"albums/{album_id}.jpg"
    if not file_exists_on_s3(IMAGES_BUCKET, cover_key):
        cover_key = ""

    create_album(album_id, name, artists, genres, cover_key)

    songs = []
    for song in body.get("songs", []):
        song_id = song["song_id"]
        audio_key = f"songs/{song_id}.mp3"
        name = song["name"]
        artists = song["artists"]
        genres = song["genres"]

        if not file_exists_on_s3(AUDIO_BUCKET, audio_key):
            return response(400, error=f"Song audio for {song_id} not found")

        artists, message = get_artist_objects(artists)
        if not artists: return response(400, error=message)

        genres, message = get_genre_objects(genres)
        if genres is None: return response(400, error=message)

        core_song = {
            "content_id": song_id,
            "content_type": "SONG",
            "name": name,
            "name_lc": name.lower(),
            "audio_key": audio_key,
            "artists": artists,
            "genres": genres
        }

        if cover_key:
            core_song["cover_key"] = cover_key

        songs.append(core_song)

    create_songs(album_id, songs)

    return response(200, error="Success")
