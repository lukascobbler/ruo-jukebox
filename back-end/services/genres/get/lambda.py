from pre_authorize import pre_authorize
from read import list_by_genre
from general_utils import response


@pre_authorize(["Admin", "User"])
def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    genre_id = path_params.get("id")

    if not genre_id:
        return response(400, error="Missing genre ID")

    return response(200, list_by_genre(genre_id))