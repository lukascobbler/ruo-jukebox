from pre_authorize import pre_authorize
from read import get_subscriptions_for_user, get_contents
from general_utils import response

def _strip_sub_prefix(val: str | None) -> str | None:
    if not val:
        return None
    return val[4:] if val.startswith("SUB~") else val

@pre_authorize(["Admin","User"])
def lambda_handler(event, context):
    user_id = event["userId"]

    # get all subscriptions
    subs = get_subscriptions_for_user(user_id)
    rows_genre  = subs.get("genres", []) or []
    rows_artist = subs.get("artists", []) or []

    # remove sub from ids
    genre_ids  = [ _strip_sub_prefix(r.get("sub_id") or r.get("SK")) for r in rows_genre  ]
    artist_ids = [ _strip_sub_prefix(r.get("sub_id") or r.get("SK")) for r in rows_artist ]
    def _dedup(xs):
        seen, out = set(), []
        for x in xs:
            if x and x not in seen:
                seen.add(x); out.append(x)
        return out
    genre_ids, artist_ids = _dedup(genre_ids), _dedup(artist_ids)

    # get names for genres and artists
    topic_ids = genre_ids + artist_ids
    meta_items = get_contents(topic_ids) if topic_ids else []
    name_by_id = { it["PK"]: it.get("name") for it in meta_items if "PK" in it }


    out = {
        "genres": [
            {"id": gid, "name": name_by_id.get(gid, None)}
            for gid in genre_ids
        ],
        "artists": [
            {"id": aid, "name": name_by_id.get(aid, None)}
            for aid in artist_ids
        ]
    }
    return response(200, out)