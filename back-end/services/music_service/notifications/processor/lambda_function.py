import os, json, boto3

dynamodb = boto3.resource("dynamodb")
SUBS    = dynamodb.Table(os.environ["SUBSCRIPTIONS_TABLE"])
ARTISTS = dynamodb.Table(os.environ["ARTISTS_TABLE"])
ALBUMS  = dynamodb.Table(os.environ["ALBUMS_TABLE"])
TRACKS  = dynamodb.Table(os.environ["TRACKS_TABLE"])
TA      = dynamodb.Table(os.environ["TRACK_ARTISTS_TABLE"])

cognito = boto3.client("cognito-idp")
sesv2   = boto3.client("sesv2")

USER_POOL_ID = os.environ["USER_POOL_ID"]
FROM_EMAIL   = os.environ["FROM_EMAIL"]

def _get_email(user_id: str) -> str | None:
    # Cognito "sub" == user_id
    try:
        resp = cognito.admin_get_user(UserPoolId=USER_POOL_ID, Username=user_id)
        for attr in resp.get("UserAttributes", []):
            if attr["Name"] == "email":
                return attr["Value"]
    except Exception:
        return None
    return None

def _send_email(to_addr: str, subject: str, text_body: str, html_body: str | None = None):
    sesv2.send_email(
        FromEmailAddress=FROM_EMAIL,
        Destination={"ToAddresses":[to_addr]},
        Content={
            "Simple": {
                "Subject": {"Data": subject},
                "Body": {
                    "Text": {"Data": text_body},
                    **({"Html": {"Data": html_body}} if html_body else {})
                }
            }
        }
    )

def _artist_info_for_track(track_id: str):
    # track may have multiple artists; notify all subscribers of all involved
    r = TA.query(KeyConditionExpression=boto3.dynamodb.conditions.Key("track_id").eq(track_id))
    artist_ids = [it["artist_id"] for it in r.get("Items", [])]
    return artist_ids

def lambda_handler(event, context):
    for rec in event["Records"]:
        msg = json.loads(rec["body"])
        typ = msg.get("type")

        if typ == "ALBUM_CREATED":
            album_id = msg["album_id"]
            # load album + artist
            ar = ALBUMS.get_item(Key={"album_id": album_id}).get("Item", {})
            if not ar: continue
            artist_id = ar.get("artist_id")
            album_name = ar.get("name")
            # artist name for mail
            artist = ARTISTS.get_item(Key={"artist_id": artist_id}).get("Item", {})
            artist_name = artist.get("name","Artist")
            subject = f"New album: {artist_name} – {album_name}"
            text = f"{artist_name} released a new album: {album_name}\nOpen the app to listen."
            _notify_subscribers(artist_id, subject, text)

        elif typ == "TRACK_CREATED":
            track_id  = msg["track_id"]
            # title
            tr = TRACKS.get_item(Key={"track_id": track_id}).get("Item", {})
            if not tr: continue
            title = tr.get("title","New single")
            # find all artists for this track and notify each artist's subscribers
            artist_ids = _artist_info_for_track(track_id)
            for artist_id in artist_ids:
                artist = ARTISTS.get_item(Key={"artist_id": artist_id}).get("Item", {})
                artist_name = artist.get("name","Artist")
                subject = f"New single: {artist_name} – {title}"
                text = f"{artist_name} released a new single: {title}\nOpen the app to listen."
                _notify_subscribers(artist_id, subject, text)

def _notify_subscribers(artist_id: str, subject: str, text: str):
    # list subscribers for artist
    r = SUBS.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("artist_id").eq(artist_id)
    )
    subs = r.get("Items", [])
    for it in subs:
        email = _get_email(it["user_id"])
        if email:
            try:
                _send_email(email, subject, text)
            except Exception:
                # swallow per-user send failures
                pass
