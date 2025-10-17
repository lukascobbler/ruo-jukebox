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


class BackendStack(Stack):
    def __init__(self, scope: Construct, id: str, dynamo_db, cognito, env, **kwargs):
        super().__init__(scope, id, **kwargs)

        auth_kwargs = cognito.auth_kwargs

        # Artists

        # Albums


        # Tracks / content


        # Genres

        # Playlists

        # Ratings API (stream takes care of aggregation)


        # Subscriptions

        
        # TODO setup deletion sqs and setup

        # stream workers
        # 1 New content (Albums + Tracks) -> notify subscribers, add feed cards, start transcription for tracks
        content_events_fn = _lambda.Function(
            self, "ContentEvents",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_content_change"),
            environment=env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )

        for t in [dynamo_db.albums, dynamo_db.tracks, dynamo_db.artists, dynamo_db.users, dynamo_db.content_genres,
                  dynamo_db.subscriptions, dynamo_db.feed, dynamo_db.transcriptions]:
            t.grant_read_write_data(content_events_fn)
        dynamo_db.audio_bucket.grant_read(content_events_fn)       # if you kick off Transcribe on S3 media
        dynamo_db.images_bucket.grant_read(content_events_fn)
        dynamo_db.transcripts_bucket.grant_read_write(content_events_fn)

        # SES + Cognito lookup + start transcription
        content_events_fn.add_to_role_policy(iam.PolicyStatement(actions=["ses:SendEmail","ses:SendRawEmail"], resources=["*"]))
        content_events_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["cognito-idp:AdminGetUser"],
            resources=[f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{user_pool.user_pool_id}"]
        ))
        content_events_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["transcribe:StartTranscriptionJob"], resources=["*"]
        ))

        # DLQs for each stream mapping
        albums_stream_dlq = sqs.Queue(self, "AlbumsStreamDLQ", retention_period=Duration.days(14))
        tracks_stream_dlq = sqs.Queue(self, "TracksStreamDLQ", retention_period=Duration.days(14))

        content_events_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.albums,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True, # if error, split batch and try again
            on_failure=lambda_events.SqsDlq(albums_stream_dlq), # where to send failed items (dead letter queue)
            report_batch_item_failures=True, # if some fail, return the failures and aws tries again
        ))
        content_events_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.tracks,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(tracks_stream_dlq),
            report_batch_item_failures=True,
        ))

        # Ratings aggregator (Ratings stream NEW_AND_OLD_IMAGES -> update target entities)
        ratings_agg_fn = _lambda.Function(
            self, "RatingsAggregator",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_ratings_change"),
            environment=env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )
        ratings_stream_dlq = sqs.Queue(self, "RatingsStreamDLQ", retention_period=Duration.days(14))
        ratings_agg_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.ratings,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(ratings_stream_dlq),
            report_batch_item_failures=True,
        ))

        # entity tables updated by aggregator
        dynamo_db.tracks.grant_read_write_data(ratings_agg_fn)
        dynamo_db.albums.grant_read_write_data(ratings_agg_fn)
        dynamo_db.artists.grant_read_write_data(ratings_agg_fn)
        dynamo_db.playlists.grant_read_write_data(ratings_agg_fn)


        # feed builders from user activity and subscriptions
        interactions_feed_fn = _lambda.Function(
            self, "InteractionsFeed",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_interaction"),
            environment=env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )
        inter_stream_dlq = sqs.Queue(self, "InteractionsStreamDLQ", retention_period=Duration.days(14))
        interactions_feed_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.interactions,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(inter_stream_dlq),
            report_batch_item_failures=True,
        ))
        for t in [dynamo_db.tracks, dynamo_db.albums, dynamo_db.artists, dynamo_db.feed]:
            t.grant_read_write_data(interactions_feed_fn)

        subs_feed_fn = _lambda.Function(
            self, "SubscriptionsFeed",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_subscription_change"),
            environment=env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )
        for t in [dynamo_db.artists, dynamo_db.albums, dynamo_db.feed]:
            t.grant_read_write_data(subs_feed_fn)
        subs_stream_dlq = sqs.Queue(self, "SubscriptionsStreamDLQ", retention_period=Duration.days(14))
        subs_feed_fn.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db.subscriptions,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(subs_stream_dlq),
            report_batch_item_failures=True,
        ))

        # API gateway

        # Artists

        # Albums


        # Content (tracks & singles)

        # Ratings (generic key built inside lambda)


        # Genres

        # Playlists

        # može i ovako, ne mora se koristiti construct ako je nešto jednostavno
        # processor_lambda = _lambda.Function(
        #     self, "ProcessorLambda",
        #     runtime=_lambda.Runtime.PYTHON_3_11,
        #     handler="lambda_function.lambda_handler",
        #     code=_lambda.Code.from_asset("lambdas/processor"),
        #     environment={"TABLE_NAME": table.table_name}
        # )

        # processor_lambda = LambdaWithSqs(self, "ProcessorLambda", queue=queue,
        #                                  handler_path="services/demo_service/processor",
        #                                  env={"TABLE_NAME": db.table_name})


        # not needed because we have made special construct to be reused
        # SQS Trigger
        # processor_lambda.add_event_source(lambda_event_sources.SqsEventSource(queue))
