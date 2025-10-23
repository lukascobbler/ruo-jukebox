import os, json, boto3

from read import (
    get_users_for_subscription,
    batch_get_items,
    userdata_table,
)

sqs = boto3.client("sqs")
EMAIL_SEND_QUEUE_URL = os.environ["EMAIL_SEND_QUEUE_URL"]

# extract data helpers

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

def _emails_for_users(user_ids):
    if not user_ids:
        return []

    keys = [{"user_id": uid, "SK": "META"} for uid in user_ids]
    rows = batch_get_items(userdata_table, keys)  # uses your read.py helper
    emails = []
    for r in rows:
        email = r.get("email")
        if email:
            emails.append(email)
    return emails

def _send_email_jobs(to_emails, payload):
    # payload is dict with {name, artist_names, genre_names}
    # SubsSendEmail will format like the old notify_new_content.
    for i in range(0, len(to_emails), 10):
        batch = to_emails[i:i+10]
        entries = []
        for j, to in enumerate(batch):
            msg = dict(payload)
            msg["to"] = to
            entries.append({
                "Id": f"{i}-{j}",
                "MessageBody": json.dumps(msg)
            })
        sqs.send_message_batch(QueueUrl=EMAIL_SEND_QUEUE_URL, Entries=entries)



def lambda_handler(event, context):
    for record in event.get("Records", []):
        try:
            body = json.loads(record["body"])
        except Exception:
            continue

        name          = body.get("name", "New content")
        artist_ids    = body.get("artist_ids", [])     
        genre_ids     = body.get("genre_ids", [])       
        artist_names  = body.get("artist_names", [])
        genre_names   = body.get("genre_names", [])

        user_ids = _gather_subscriber_user_ids(artist_ids, genre_ids)

        if not user_ids:
            continue

        emails = _emails_for_users(list(user_ids))
        if not emails:
            continue

        payload = {
            "name": name,
            "artist_names": artist_names,
            "genre_names": genre_names
        }
        _send_email_jobs(emails, payload)

