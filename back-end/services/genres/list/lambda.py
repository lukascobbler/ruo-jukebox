import os
from dataclasses import asdict
import boto3
from boto3.dynamodb.conditions import Key
from services.common import _response
from services.genres.list.model.model import GenreItem

TABLE_NAME = os.environ['GENRES_TABLE']
dynamodb = boto3.resource('dynamodb')
genres_table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    response = genres_table.query(
        KeyConditionExpression=Key("PK").eq("genres")
    )
    items = response.get("Items", [])
    genres = [
        asdict(GenreItem(
            id=item.get("genre_id"),
            name=item.get("Name"),
            isSubscribed=None
        ))
        for item in items
    ]
    return _response(200, genres)
