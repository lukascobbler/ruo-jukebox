from constructs import Construct
from aws_cdk import (
    Stack, Duration, RemovalPolicy,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_events,
    aws_apigateway as apigw,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_certificatemanager as acm
)

from iac.dynamo_db_stack import DynamoDbStack
from iac.s3_stack import S3Stack


def mk_lambda(self, logical_id: str, path: str, env: dict, dynamo_db: DynamoDbStack, s3: S3Stack, extra_env: dict | None = None) -> _lambda.Function:
    env = {**env, **(extra_env or {})}
    fn = _lambda.Function(
        self, logical_id,
        runtime=_lambda.Runtime.PYTHON_3_11,
        handler="lambda_function.lambda_handler",
        code=_lambda.Code.from_asset(path),
        environment=env,
        timeout=Duration.seconds(15),
        memory_size=256,
    )
    # grants TODO right now everyone gets everything
    s3.audio_bucket.grant_read_write(fn)
    s3.images_bucket.grant_read_write(fn)
    s3.transcripts_bucket.grant_read_write(fn)
    for t in [
        dynamo_db.artists, dynamo_db.albums, dynamo_db.tracks, dynamo_db.track_artists, dynamo_db.genres,
        dynamo_db.content_genres, dynamo_db.users, dynamo_db.playlists, dynamo_db.playlist_items,
        dynamo_db.ratings, dynamo_db.subscriptions, dynamo_db.interactions, dynamo_db.feed,
        dynamo_db.transcriptions
    ]:
        t.grant_read_write_data(fn)
    return fn