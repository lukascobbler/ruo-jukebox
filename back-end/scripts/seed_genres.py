from boto3.dynamodb.conditions import Key
import boto3, uuid, argparse

genres = [
    "Rock", "Pop", "Jazz", "Blues", "Classical", "Electronic",
    "Hip-Hop", "Metal", "Latin", "Soul", "Country", "Reggae"
]


def query_all(table, **kwargs):
    items = []
    resp = table.query(**kwargs)
    items.extend(resp["Items"])
    while "LastEvaluatedKey" in resp:
        resp = table.query(ExclusiveStartKey=resp["LastEvaluatedKey"], **kwargs)
        items.extend(resp["Items"])
    return items


def delete_all_genres(table):
    items = query_all(table, IndexName="byType", KeyConditionExpression=Key("content_type").eq("GENRE"))
    with table.batch_writer() as batch:
        for i in items:
            batch.delete_item(Key={"PK": i["PK"], "SK": i["SK"]})
    print(f"Deleted {len(items)} existing genres.")


def create_genre(table, name):
    genre_id = f"GENRE~{uuid.uuid4()}"
    item = {
        "PK": genre_id,
        "SK": "META",
        "genre_id": genre_id,
        "content_type": "GENRE",
        "name": name
    }
    table.put_item(Item=item)
    return item


def reset_genres(branch: str):
    suffix = f"-{branch}" if branch != "main" else ""
    table_name = f"ContentTable{suffix}"
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    print(f"Using table: {table_name}")
    delete_all_genres(table)
    for g in genres:
        create_genre(table, g)
        print(f"Created genre: {g}")
    print("Genres reset complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset all genres in ContentTable with optional branch suffix.")
    parser.add_argument("--branch", default="main", help="Branch name for environment suffix (default: main)")
    args = parser.parse_args()
    reset_genres(args.branch)
