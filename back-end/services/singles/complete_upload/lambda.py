from general_utils import response, file_exists_on_s3, get_genre_objects, get_artist_objects
from create import create_single, create_songs
from read import get_users_for_subscription
from pre_authorize import pre_authorize
import json, os, boto3

AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGES_BUCKET = os.environ["IMAGES_BUCKET"]
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


@pre_authorize(['Admin'])
def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    single_id = body.get("single_id").strip()
    song_id = body.get("song_id").strip()
    name = body.get("name").strip()
    artist_ids = body.get("artists")
    genre_ids = body.get("genres")

    if not single_id: return response(400, error="Field 'single_id' is required")
    if not song_id: return response(400, error="Field 'song_id' is required")
    if not name: return response(400, error="Field 'name' is required")

    audio_key = f"songs/{song_id}.mp3"
    if not file_exists_on_s3(AUDIO_BUCKET, audio_key):
        return response(400, error="Song audio not found")

    cover_key = f"singles/{single_id}.jpg"
    if not file_exists_on_s3(IMAGES_BUCKET, cover_key):
        cover_key = ""

    genres, message = get_genre_objects(genre_ids)
    if genres is None: return response(400, error=message)

    artists, message = get_artist_objects(artist_ids)
    if artists is None: return response(400, error=message)

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

    core_single = create_single(single_id, name, artists, genres, audio_key, cover_key, song_id)
    create_songs(single_id, [core_song])

    msg = {
        "type": "single",
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

    return response(200, core_single)
