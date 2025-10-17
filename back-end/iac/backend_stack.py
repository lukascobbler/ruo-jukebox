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
        genres_create = self.mk_lambda("GenresCreate", "services/music_service/genres/create", env)
        genres_list   = self.mk_lambda("GenresList",   "services/music_service/genres/list", env)
        genres_get    = self.mk_lambda("GenresGet",    "services/music_service/genres/get", env)
        genres_update = self.mk_lambda("GenresUpdate", "services/music_service/genres/update", env)
        genres_delete = self.mk_lambda("GenresDelete", "services/music_service/genres/delete", env)

        # Playlists
        playlists_create       = self.mk_lambda("PlaylistsCreate",     "services/music_service/playlists/create", env)
        playlists_list_mine    = self.mk_lambda("PlaylistsListMine","services/music_service/playlists/list_mine", env)
        playlists_get          = self.mk_lambda("PlaylistsGet",        "services/music_service/playlists/get", env)
        playlists_update       = self.mk_lambda("PlaylistsUpdate",     "services/music_service/playlists/update", env)
        playlists_delete       = self.mk_lambda("PlaylistsDelete",     "services/music_service/playlists/delete", env)
        playlists_add_track    = self.mk_lambda("PlaylistsAddTrack",    "services/music_service/playlists/add_track", env)
        playlists_remove_track = self.mk_lambda("PlaylistsRemoveTrack", "services/music_service/playlists/remove_track", env)

        # Ratings API (stream takes care of aggregation)
        ratings_put    = self.mk_lambda("RatingsPut",    "services/music_service/ratings/put", env)
        ratings_delete = self.mk_lambda("RatingsDelete", "services/music_service/ratings/delete", env)

        # Subscriptions
        subs_create = self.mk_lambda("SubsCreate",    "services/music_service/subscriptions/create", env)
        subs_list   = self.mk_lambda("SubsListMine",  "services/music_service/subscriptions/list_mine", env)
        subs_delete = self.mk_lambda("SubsDelete",    "services/music_service/subscriptions/delete", env)

        
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
        rating = content_id.add_resource("rating")
        rating.add_method("PUT",    apigw.LambdaIntegration(ratings_put),    **auth_kwargs)
        rating.add_method("DELETE", apigw.LambdaIntegration(ratings_delete), **auth_kwargs)

        # Genres
        genres = api.root.add_resource("genres")
        genres.add_method("POST", apigw.LambdaIntegration(genres_create), **auth_kwargs)
        genres.add_method("GET",  apigw.LambdaIntegration(genres_list),   **auth_kwargs)
        genre_id = genres.add_resource("{id}")
        genre_id.add_method("GET",    apigw.LambdaIntegration(genres_get),    **auth_kwargs)
        genre_id.add_method("PATCH",  apigw.LambdaIntegration(genres_update), **auth_kwargs)
        genre_id.add_method("DELETE", apigw.LambdaIntegration(genres_delete), **auth_kwargs)

        # Playlists
        playlists = api.root.add_resource("playlists")
        playlists.add_method("POST", apigw.LambdaIntegration(playlists_create), **auth_kwargs)
        playlists.add_method("GET",  apigw.LambdaIntegration(playlists_list_mine), **auth_kwargs)
        pl_id = playlists.add_resource("{id}")
        pl_id.add_method("GET",    apigw.LambdaIntegration(playlists_get),    **auth_kwargs)
        pl_id.add_method("PATCH",  apigw.LambdaIntegration(playlists_update), **auth_kwargs)
        pl_id.add_method("DELETE", apigw.LambdaIntegration(playlists_delete), **auth_kwargs)
        pl_tracks = pl_id.add_resource("tracks")
        pl_tracks.add_method("POST", apigw.LambdaIntegration(playlists_add_track), **auth_kwargs)
        pl_trk_id = pl_tracks.add_resource("{trackId}")
        pl_trk_id.add_method("DELETE", apigw.LambdaIntegration(playlists_remove_track), **auth_kwargs)

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
