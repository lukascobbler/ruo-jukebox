from general_utils import response, file_exists_on_s3, get_genre_objects, get_artist_objects, generate_s3_download_url
from create import create_album, create_songs
from read import get_users_for_subscription
from mutagen.mp3 import MP3
import json, os, boto3
from io import BytesIO
import requests

IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
SUB_SQS_QUEUE_URL = os.environ["SUB_QUEUE_URL"]
FEED_SQS_QUEUE_URL = os.environ["FEED_QUEUE_URL"]
sqs = boto3.client("sqs")


def _gather_subscriber_user_ids(artist_ids, genre_ids):
    user_ids = set()

    for aid in (artist_ids or []):
        for row in get_users_for_subscription(aid):
            uid = row.get("user_id")
            if uid:
                user_ids.add(uid)

    for gid in (genre_ids or []):
        for row in get_users_for_subscription(gid):
            uid = row.get("user_id")
            if uid:
                user_ids.add(uid)

    return user_ids


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    album_id = body.get("album_id")
    name = body.get("name")

    artist_ids = body.get("artists")
    genre_ids = body.get("genres")

    if not album_id: return response(400, error="Field 'album_id' is required")
    if not name: return response(400, error="Field 'name' is required")

    artists, message = get_artist_objects(artist_ids)
    if artists is None: return response(400, error=message)

    genres, message = get_genre_objects(genre_ids)
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

        audio_url = generate_s3_download_url(AUDIO_BUCKET, audio_key)
        mp3_response = requests.get(audio_url)
        audio = MP3(BytesIO(mp3_response.content))
        duration_seconds = int(audio.info.length)

        core_song = {
            "content_id": song_id,
            "name": name,
            "name_lc": name.lower(),
            "audio_key": audio_key,
            "artists": artists,
            "genres": genres,
            "album_id": album_id,
            "duration": duration_seconds
        }

        if cover_key:
            core_song["cover_key"] = cover_key

        songs.append(core_song)

    create_songs(album_id, songs)

    msg = {
        "type": "album",
        "name": name,
        "artist_ids": [a["artist_id"] for a in artists],
        "genre_ids": [g["genre_id"] for g in genres],
        "artist_names": [a["name"] for a in artists],
        "genre_names": [g["name"] for g in genres]
    }

    sqs.send_message(QueueUrl=SUB_SQS_QUEUE_URL, MessageBody=json.dumps(msg))

    user_ids = _gather_subscriber_user_ids(artist_ids, genre_ids)
    entries = [{"Id": user_id, "MessageBody": user_id} for user_id in user_ids]
    response = sqs.send_message_batch(QueueUrl=FEED_SQS_QUEUE_URL, Entries=entries)

    return response(200, error="Success")
