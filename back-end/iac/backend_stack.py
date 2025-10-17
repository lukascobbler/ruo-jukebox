from iac.constructs.lambda_with_sqs import LambdaWithSqs
from constructs import Construct
from aws_cdk import (
    Stack, Duration, RemovalPolicy,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_events,
    aws_apigateway as apigw,
    aws_cognito as cognito,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_certificatemanager as acm
)


class BackendStack(Stack):
    def __init__(self, scope: Construct, id: str, db, **kwargs):
        super().__init__(scope, id, **kwargs)

        # cognito setup withhout verification and groups
        user_pool = cognito.UserPool(
            self, "UserPool",
            self_sign_up_enabled=True, # users register themselves
            sign_in_aliases=cognito.SignInAliases(username=True, email=True), # use either username or email to sign in (we can change it)
            standard_attributes=cognito.StandardAttributes( # required attributes
                given_name=cognito.StandardAttribute(required=True, mutable=True), 
                family_name=cognito.StandardAttribute(required=True, mutable=True),
                birthdate=cognito.StandardAttribute(required=True, mutable=True),
                email=cognito.StandardAttribute(required=True, mutable=True),
            ),
            password_policy=cognito.PasswordPolicy(min_length=8),
            removal_policy=RemovalPolicy.DESTROY,
        )
        user_pool_client = user_pool.add_client(
            "WebClient",
            generate_secret=False,
            prevent_user_existence_errors=True,
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True),
        )
        cognito.CfnUserPoolGroup(self, "UsersGroup",  group_name="user",  user_pool_id=user_pool.user_pool_id) # used in lambdas to check permissions
        cognito.CfnUserPoolGroup(self, "AdminsGroup", group_name="admin", user_pool_id=user_pool.user_pool_id)

        # pre-signup trigger lambda, auto-confirms email for cognito
        pre_signup = _lambda.Function(
            self, "CognitoPreSignUp",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="pre_signup.lambda_handler",
            code=_lambda.Code.from_asset("services/auth/pre_signup"),
            timeout=Duration.seconds(5),
            memory_size=128,
        )
        user_pool.add_trigger(cognito.UserPoolOperation.PRE_SIGN_UP, pre_signup)

        # post-confirm trigger lambda adds user to "user" group
        post_confirm = _lambda.Function(
            self, "CognitoPostConfirm",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="post_confirm.lambda_handler",
            code=_lambda.Code.from_asset("services/auth/post_confirm"),
            environment={
                "USER_POOL_ID": user_pool.user_pool_id,
                "DEFAULT_GROUP": "user",
            },
            timeout=Duration.seconds(10),
            memory_size=256,
        )
        user_pool.add_trigger(cognito.UserPoolOperation.POST_CONFIRMATION, post_confirm)
        post_confirm.add_to_role_policy(iam.PolicyStatement(
            actions=["cognito-idp:AdminAddUserToGroup"],
            resources=[f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{user_pool.user_pool_id}"]
        ))

        # API authorizer
        authorizer = apigw.CognitoUserPoolsAuthorizer(self, "ApiAuthorizer", cognito_user_pools=[user_pool]) 
        auth_kwargs = dict(authorizer=authorizer, authorization_type=apigw.AuthorizationType.COGNITO) # binds to routes, now in the lambda the user claims can be taken from cognito authorizer

        common_env = {
            "AUDIO_BUCKET": db.audio_bucket.bucket_name,
            "IMAGES_BUCKET": db.images_bucket.bucket_name,
            "TRANSCRIPTS_BUCKET": db.transcripts_bucket.bucket_name,
            "ARTISTS_TABLE": db.artists.table_name,
            "ALBUMS_TABLE": db.albums.table_name,
            "TRACKS_TABLE": db.tracks.table_name,
            "TRACK_ARTISTS_TABLE": db.track_artists.table_name,
            "GENRES_TABLE": db.genres.table_name,
            "CONTENT_GENRES_TABLE": db.content_genres.table_name,
            "USERS_TABLE": db.users.table_name,
            "PLAYLISTS_TABLE": db.playlists.table_name,
            "PLAYLIST_ITEMS_TABLE": db.playlist_items.table_name,
            "RATINGS_TABLE": db.ratings.table_name,
            "SUBSCRIPTIONS_TABLE": db.subscriptions.table_name,
            "INTERACTIONS_TABLE": db.interactions.table_name,
            "FEED_TABLE": db.feed.table_name,
            "TRANSCRIPTIONS_TABLE": db.transcriptions.table_name,
            "USER_POOL_ID": user_pool.user_pool_id,
            "USER_POOL_CLIENT_ID": user_pool_client.user_pool_client_id,
            # Email (SES verified sender) TODO wtf
            "FROM_EMAIL": "no-reply@jukebox.example.com",
        }

        # lambda setup helper
        def mk_lambda(logical_id: str, path: str, extra_env: dict | None = None) -> _lambda.Function:
            env = {**common_env, **(extra_env or {})}
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
            db.audio_bucket.grant_read_write(fn)
            db.images_bucket.grant_read_write(fn)
            db.transcripts_bucket.grant_read_write(fn)
            for t in [
                db.artists, db.albums, db.tracks, db.track_artists, db.genres,
                db.content_genres, db.users, db.playlists, db.playlist_items,
                db.ratings, db.subscriptions, db.interactions, db.feed, db.transcriptions
            ]:
                t.grant_read_write_data(fn)
            return fn

        # Artists
        artists_create = mk_lambda("ArtistsCreate", "services/music_service/artists/create")
        artists_list   = mk_lambda("ArtistsList",   "services/music_service/artists/list")
        artists_get    = mk_lambda("ArtistsGet",    "services/music_service/artists/get")
        artists_update = mk_lambda("ArtistsUpdate", "services/music_service/artists/update")
        artists_delete = mk_lambda("ArtistsDelete", "services/music_service/artists/delete")

        # Albums
        albums_create   = mk_lambda("AlbumsCreate",  "services/music_service/albums/create")
        albums_list     = mk_lambda("AlbumsList",    "services/music_service/albums/list")
        albums_get      = mk_lambda("AlbumsGet",     "services/music_service/albums/get")
        albums_update   = mk_lambda("AlbumsUpdate",  "services/music_service/albums/update")
        albums_delete   = mk_lambda("AlbumsDelete",  "services/music_service/albums/delete")
        albums_cov_init = mk_lambda("AlbumsCoverInit", "services/music_service/albums/init_cover_upload")
        albums_cov_done = mk_lambda("AlbumsCoverDone", "services/music_service/albums/complete_cover")

        # Tracks / content
        content_init   = mk_lambda("ContentInitUpload",    "services/music_service/content/init_upload")
        content_done   = mk_lambda("ContentCompleteUpload","services/music_service/content/complete_upload")
        content_list   = mk_lambda("ContentList",          "services/music_service/content/list")
        content_get    = mk_lambda("ContentGet",           "services/music_service/content/get")
        content_update = mk_lambda("ContentUpdate",        "services/music_service/content/update")
        content_delete = mk_lambda("ContentDelete",        "services/music_service/content/delete")
        track_cov_init = mk_lambda("TrackCoverInit",       "services/music_service/content/init_cover_upload")
        track_cov_done = mk_lambda("TrackCoverDone",       "services/music_service/content/complete_cover")

        # Genres
        genres_create = mk_lambda("GenresCreate", "services/music_service/genres/create")
        genres_list   = mk_lambda("GenresList",   "services/music_service/genres/list")
        genres_get    = mk_lambda("GenresGet",    "services/music_service/genres/get")
        genres_update = mk_lambda("GenresUpdate", "services/music_service/genres/update")
        genres_delete = mk_lambda("GenresDelete", "services/music_service/genres/delete")

        # Playlists
        playlists_create = mk_lambda("PlaylistsCreate",     "services/music_service/playlists/create")
        playlists_list_mine = mk_lambda("PlaylistsListMine","services/music_service/playlists/list_mine")
        playlists_get    = mk_lambda("PlaylistsGet",        "services/music_service/playlists/get")
        playlists_update = mk_lambda("PlaylistsUpdate",     "services/music_service/playlists/update")
        playlists_delete = mk_lambda("PlaylistsDelete",     "services/music_service/playlists/delete")
        playlists_add_track    = mk_lambda("PlaylistsAddTrack",    "services/music_service/playlists/add_track")
        playlists_remove_track = mk_lambda("PlaylistsRemoveTrack", "services/music_service/playlists/remove_track")

        # Ratings API (stream takes care of aggregation)
        ratings_put    = mk_lambda("RatingsPut",    "services/music_service/ratings/put")
        ratings_delete = mk_lambda("RatingsDelete", "services/music_service/ratings/delete")

        # Subscriptions
        subs_create = mk_lambda("SubsCreate",    "services/music_service/subscriptions/create")
        subs_list   = mk_lambda("SubsListMine",  "services/music_service/subscriptions/list_mine")
        subs_delete = mk_lambda("SubsDelete",    "services/music_service/subscriptions/delete")

        
        # TODO setup deletion sqs and setup

        # stream workers
        # 1 New content (Albums + Tracks) -> notify subscribers, add feed cards, start transcription for tracks
        content_events_fn = _lambda.Function(
            self, "ContentEvents",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_content_change"),
            environment=common_env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )

        for t in [db.albums, db.tracks, db.artists, db.users, db.content_genres,
                  db.subscriptions, db.feed, db.transcriptions]:
            t.grant_read_write_data(content_events_fn)
        db.audio_bucket.grant_read(content_events_fn)       # if you kick off Transcribe on S3 media
        db.images_bucket.grant_read(content_events_fn)
        db.transcripts_bucket.grant_read_write(content_events_fn)

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
            db.albums,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True, # if error, split batch and try again
            on_failure=lambda_events.SqsDlq(albums_stream_dlq), # where to send failed items (dead letter queue)
            report_batch_item_failures=True, # if some fail, return the failures and aws tries again
        ))
        content_events_fn.add_event_source(lambda_events.DynamoEventSource(
            db.tracks,
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
            environment=common_env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )
        ratings_stream_dlq = sqs.Queue(self, "RatingsStreamDLQ", retention_period=Duration.days(14))
        ratings_agg_fn.add_event_source(lambda_events.DynamoEventSource(
            db.ratings,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(ratings_stream_dlq),
            report_batch_item_failures=True,
        ))

        # entity tables updated by aggregator
        db.tracks.grant_read_write_data(ratings_agg_fn)
        db.albums.grant_read_write_data(ratings_agg_fn)
        db.artists.grant_read_write_data(ratings_agg_fn)
        db.playlists.grant_read_write_data(ratings_agg_fn)


        # feed builders from user activity and subscriptions
        interactions_feed_fn = _lambda.Function(
            self, "InteractionsFeed",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_interaction"),
            environment=common_env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )
        inter_stream_dlq = sqs.Queue(self, "InteractionsStreamDLQ", retention_period=Duration.days(14))
        interactions_feed_fn.add_event_source(lambda_events.DynamoEventSource(
            db.interactions,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(inter_stream_dlq),
            report_batch_item_failures=True,
        ))
        for t in [db.tracks, db.albums, db.artists, db.feed]:
            t.grant_read_write_data(interactions_feed_fn)

        subs_feed_fn = _lambda.Function(
            self, "SubscriptionsFeed",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("services/streams/on_subscription_change"),
            environment=common_env,
            timeout=Duration.seconds(60),
            memory_size=512,
        )
        for t in [db.artists, db.albums, db.feed]:
            t.grant_read_write_data(subs_feed_fn)
        subs_stream_dlq = sqs.Queue(self, "SubscriptionsStreamDLQ", retention_period=Duration.days(14))
        subs_feed_fn.add_event_source(lambda_events.DynamoEventSource(
            db.subscriptions,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=100,
            max_batching_window=Duration.seconds(1),
            retry_attempts=3,
            bisect_batch_on_error=True,
            on_failure=lambda_events.SqsDlq(subs_stream_dlq),
            report_batch_item_failures=True,
        ))

        # API gateway
        api = apigw.RestApi(
            self, "DemoApi",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,  # TODO change
                allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
                allow_headers=apigw.Cors.DEFAULT_HEADERS
            ),
            endpoint_configuration=apigw.EndpointConfiguration(types=[apigw.EndpointType.REGIONAL]),
        )

        # Artists
        artists = api.root.add_resource("artists")
        artists.add_method("POST", apigw.LambdaIntegration(artists_create), **auth_kwargs)   # admin: check group in lambda
        artists.add_method("GET",  apigw.LambdaIntegration(artists_list),   **auth_kwargs)
        artist_id = artists.add_resource("{id}")
        artist_id.add_method("GET",    apigw.LambdaIntegration(artists_get),    **auth_kwargs)
        artist_id.add_method("PATCH",  apigw.LambdaIntegration(artists_update), **auth_kwargs)
        artist_id.add_method("DELETE", apigw.LambdaIntegration(artists_delete), **auth_kwargs)

        # Albums
        albums = api.root.add_resource("albums")
        albums.add_method("POST", apigw.LambdaIntegration(albums_create), **auth_kwargs)
        albums.add_method("GET",  apigw.LambdaIntegration(albums_list),   **auth_kwargs)
        album_id = albums.add_resource("{id}")
        album_id.add_method("GET",    apigw.LambdaIntegration(albums_get),    **auth_kwargs)
        album_id.add_method("PATCH",  apigw.LambdaIntegration(albums_update), **auth_kwargs)
        album_id.add_method("DELETE", apigw.LambdaIntegration(albums_delete), **auth_kwargs)
        albums.add_resource("init-cover-upload").add_method("POST", apigw.LambdaIntegration(albums_cov_init), **auth_kwargs)
        albums.add_resource("complete-cover").add_method("POST",    apigw.LambdaIntegration(albums_cov_done), **auth_kwargs)

        # Content (tracks & singles)
        content = api.root.add_resource("content")
        content.add_resource("init-upload").add_method("POST",     apigw.LambdaIntegration(content_init), **auth_kwargs)
        content.add_resource("complete-upload").add_method("POST", apigw.LambdaIntegration(content_done), **auth_kwargs)
        content.add_method("GET", apigw.LambdaIntegration(content_list), **auth_kwargs)
        content_id = content.add_resource("{id}")
        content_id.add_method("GET",    apigw.LambdaIntegration(content_get),    **auth_kwargs)
        content_id.add_method("PATCH",  apigw.LambdaIntegration(content_update), **auth_kwargs)
        content_id.add_method("DELETE", apigw.LambdaIntegration(content_delete), **auth_kwargs)
        content.add_resource("init-cover-upload").add_method("POST", apigw.LambdaIntegration(track_cov_init), **auth_kwargs)
        content.add_resource("complete-cover").add_method("POST",    apigw.LambdaIntegration(track_cov_done), **auth_kwargs)

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



        # Settings for custom domain
        certificate = acm.Certificate.from_certificate_arn(
            self, "ApiCert",
            "arn:aws:acm:eu-central-1:779156816822:certificate/875c9c89-5b45-4b0e-8074-80685d61308a"
        )

        domain_name = apigw.DomainName(
            self, "CustomDomain",
            domain_name="api.jukebox.moma.rs",
            certificate=certificate,
        )

        apigw.BasePathMapping(
            self, "ApiMapping",
            domain_name=domain_name,
            rest_api=api,
            base_path="",
            stage=api.deployment_stage
        )
