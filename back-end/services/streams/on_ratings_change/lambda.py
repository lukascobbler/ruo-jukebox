import os, time, json, logging
from decimal import Decimal
import boto3

log = logging.getLogger()
log.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
songs = dynamodb.Table(os.environ["SONGS_TABLE"])

def _dval(x):
    try:
        return int(x.get("N"))
    except Exception:
        return None

def lambda_handler(event, context):

    song_acc = {}

    records = event.get("Records") or []
    for r in records:
        ev = r.get("eventName")
        ddb = r.get("dynamodb") or {}
        keys = ddb.get("Keys") or {}
        newi = ddb.get("NewImage") or {}
        oldi = ddb.get("OldImage") or {}
        sid = (keys.get("song_id") or {}).get("S")

        if not sid:
            continue

        dsum = 0
        dcnt = 0

        if ev == "INSERT":
            nv = _dval(newi.get("value"))
            if nv is not None:
                dsum += nv
                dcnt += 1
        elif ev == "MODIFY":
            nv = _dval(newi.get("value"))
            ov = _dval(oldi.get("value"))
            if nv is not None and ov is not None:
                delta = nv - ov
                if delta != 0:
                    dsum += delta
        elif ev == "REMOVE":
            ov = _dval(oldi.get("value"))
            if ov is not None:
                dsum -= ov
                dcnt -= 1

        if dsum != 0 or dcnt != 0:
            bucket = song_acc.setdefault(sid, {"dsum": 0, "dcnt": 0, "event_ids": []})
            bucket["dsum"] += dsum
            bucket["dcnt"] += dcnt
            bucket["event_ids"].append(r.get("eventID"))

    failures = []

    now = int(time.time())
    for sid, agg in song_acc.items():
        try:
            songs.update_item(
                Key={"song_id": sid},
                UpdateExpression=(
                    "SET #stats.#sum = if_not_exists(#stats.#sum, :z) + :ds, "
                    "#stats.#cnt = if_not_exists(#stats.#cnt, :z) + :dc, "
                    "updated_at = :now"
                ),
                ExpressionAttributeNames={
                    "#stats": "stats",
                    "#sum": "rating_sum",
                    "#cnt": "rating_cnt",
                },
                ExpressionAttributeValues={
                    ":ds": Decimal(agg["dsum"]),
                    ":dc": Decimal(agg["dcnt"]),
                    ":z": Decimal(0),
                    ":now": now,
                },
            )
        except Exception as e:
            log.exception("Failed updating song %s aggregate", sid)
            for eid in agg["event_ids"]:
                failures.append({"itemIdentifier": eid})

    return {"batchItemFailures": failures}
