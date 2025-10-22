from pre_authorize import pre_authorize
from read import search
from general_utils import response


@pre_authorize(["Admin", "User"])
def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    query = path_params.get("query")

    if not query:
        return response(400, error="Missing query")

    return response(200, search(query))