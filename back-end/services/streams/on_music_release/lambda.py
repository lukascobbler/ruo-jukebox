import os, json, time
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeDeserializer

deser = TypeDeserializer()

dynamodb = boto3.resource("dynamodb")
ddb      = boto3.client("dynamodb")
ses      = boto3.client("ses", region_name=os.environ.get("AWS_REGION", "eu-central-1"))

ARTISTS_TBL         = dynamodb.Table(os.environ["ARTISTS_TABLE"])
ALBUMS_TBL          = dynamodb.Table(os.environ["ALBUMS_TABLE"])
SONGS_TBL           = dynamodb.Table(os.environ["SONGS_TABLE"])
CONTENT_GENRES_TBL  = dynamodb.Table(os.environ["CONTENT_GENRES_TABLE"])
SONG_ARTISTS_TBL    = dynamodb.Table(os.environ["SONG_ARTISTS_TABLE"])
SUBSCRIPTIONS_TBL   = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])
USERS_TBL           = dynamodb.Table(os.environ["USERS_TABLE"])
FEED_TBL            = dynamodb.Table(os.environ["FEED_TABLE"])

FROM_EMAIL = os.environ["FROM_EMAIL"]

CG_BY_ENTITY_GSI = "byEntity"

def _dynamo_to_py(img):
    if not img: return {}
    return {k: deser.deserialize(v) for k, v in img.items()}

def _is_insert(rec):
    return rec.get("eventName") == "INSERT"

def _get_album_genres(album_id: str) -> list[str]:
    resp = CONTENT_GENRES_TBL.query(
        IndexName=CG_BY_ENTITY_GSI,
        KeyConditionExpression=Key("entity").eq(album_id)
    )
    return [it["genre"] for it in resp.get("Items", [])]

def _get_song_genres(song_id: str) -> list[str]:
    resp = CONTENT_GENRES_TBL.query(
        IndexName=CG_BY_ENTITY_GSI,
        KeyConditionExpression=Key("entity").eq(song_id)
    )
    return [it["genre"] for it in resp.get("Items", [])]

def _get_song_artists(song_id: str) -> list[str]:
    resp = SONG_ARTISTS_TBL.query(
        KeyConditionExpression=Key("song_id").eq(song_id)
    )
    return [it["artist_id"] for it in resp.get("Items", [])]

def _get_subscribers_for_topics(topics: set[str]) -> set[str]:
    users: set[str] = set()
    for topic in topics:
        lek = None
        while True:
            kwargs = {
                "KeyConditionExpression": Key("topic").eq(topic),
                "ProjectionExpression": "topic, user_id",
            }
            if lek:
                kwargs["ExclusiveStartKey"] = lek
            resp = SUBSCRIPTIONS_TBL.query(**kwargs)
            for it in resp.get("Items", []):
                users.add(it["user_id"])
            lek = resp.get("LastEvaluatedKey")
            if not lek:
                break
    return users

def _get_artist_name(artist_id: str) -> str:
    it = ARTISTS_TBL.get_item(Key={"artist_id": artist_id}).get("Item") or {}
    return it.get("Name", "") or ""

def _get_user_email(user_id: str) -> str | None:
    it = USERS_TBL.get_item(Key={"user_id": user_id}).get("Item") or {}
    email = it.get("email")
    if email and isinstance(email, str): return email
    return None

def _put_idempotency_marker(user_id: str, kind: str, entity_id: str) -> bool:
    sk = f"EMAIL#{kind}#{entity_id}"
    try:
        FEED_TBL.put_item(
            Item={
                "user_id": user_id,
                "item_id": sk,
                "ttl": int(time.time()) + 30*24*3600,
                "created_at": int(time.time()),
                "type": "EMAIL_MARKER",
            },
            ConditionExpression="attribute_not_exists(user_id) AND attribute_not_exists(item_id)"
        )
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise

def _send_email(to_email: str, subject: str, html_body: str):
    ses.send_email(
        Source=FROM_EMAIL,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Html": {"Data": html_body}}
        }
    )

def _album_email_html(album_name: str, artist_name: str) -> str:
    return f"""
    <html><body>
      <h2>New album: {album_name}</h2>
      <p>By <b>{artist_name}</b></p>
      <p>Listen now in Jukebox 🎧</p>
    </body></html>
    """

def _single_email_html(song_title: str, artist_names: list[str]) -> str:
    by = ", ".join([n for n in artist_names if n][:3])
    return f"""
    <html><body>
      <h2>New single: {song_title}</h2>
      <p>By <b>{by}</b></p>
      <p>Listen now in Jukebox 🎧</p>
    </body></html>
    """

def _handle_album_insert(new_item: dict):
    album_id = new_item["album_id"]
    album_name = new_item.get("Name", "") or ""
    primary_artist_id = new_item.get("primary_artist_id", "")

    topics = set()
    if primary_artist_id:
        topics.add(primary_artist_id)       
    for gid in _get_album_genres(album_id):
        topics.add(gid)                      

    user_ids = _get_subscribers_for_topics(topics)
    if not user_ids: return

    artist_name = _get_artist_name(primary_artist_id) if primary_artist_id else ""

    subject = f"New album: {album_name} by {artist_name}".strip()
    body    = _album_email_html(album_name, artist_name)

    for uid in user_ids:
        if not _put_idempotency_marker(uid, "ALBUM", album_id):
            continue
        email = _get_user_email(uid)
        if not email: continue
        _send_email(email, subject, body)

def _handle_song_insert(new_item: dict):
    song_id   = new_item["song_id"]
    album_id  = new_item.get("album_id", "")
    # Only notify for singles
    if album_id and album_id != "SINGLE":
        return

    title = new_item.get("Title") or new_item.get("Name") or "New Single"

    artist_ids = _get_song_artists(song_id)

    genre_ids = _get_song_genres(song_id)

    topics = set(artist_ids) | set(genre_ids)
    user_ids = _get_subscribers_for_topics(topics)
    if not user_ids: return

    artist_names = [_get_artist_name(aid) for aid in artist_ids[:3]]
    subject = f"New single: {title}"
    body    = _single_email_html(title, artist_names)

    for uid in user_ids:
        if not _put_idempotency_marker(uid, "SINGLE", song_id):
            continue
        email = _get_user_email(uid)
        if not email: continue
        _send_email(email, subject, body)

def lambda_handler(event, context):
    for rec in event.get("Records", []):
        if not _is_insert(rec):
            continue
        new_img = _dynamo_to_py(rec["dynamodb"].get("NewImage"))
        if not new_img:
            continue

        arn = rec.get("eventSourceARN", "")
        if ":table/Albums/" in arn:
            _handle_album_insert(new_img)
        elif ":table/Songs/" in arn:
            _handle_song_insert(new_img)
        else:
            pass

    return {"batchItemFailures": []}
