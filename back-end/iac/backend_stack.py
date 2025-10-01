from iac.constructs.lambda_with_sqs import LambdaWithSqs
from constructs import Construct
from aws_cdk import (
    Stack, Duration,
    aws_sqs as sqs,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_certificatemanager as acm,
    aws_cognito as cognito,
    aws_iam as iam,
)


class BackendStack(Stack):
    def __init__(self, scope: Construct, id: str, db, **kwargs):
        super().__init__(scope, id, **kwargs)

        # SQS Queue
        queue = sqs.Queue(self, "MusicQueue", visibility_timeout=Duration.seconds(60), retention_period=Duration.days(1))


        # Cognito (email/password sign-in)
        user_pool = cognito.UserPool(
            self, "UserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True, username=True),
            standard_attributes=cognito.StandardAttributes(
                given_name=cognito.StandardAttribute(required=True, mutable=True),
                family_name=cognito.StandardAttribute(required=True, mutable=True),
                birthdate=cognito.StandardAttribute(required=True, mutable=True),
            ),
            password_policy=cognito.PasswordPolicy(min_length=8),
        )
        user_pool_client = user_pool.add_client(
            "WebClient",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True),
            prevent_user_existence_errors=True,
        )

        # Groups (roles)
        cognito.CfnUserPoolGroup(self, "AdminsGroup", group_name="admin", user_pool_id=user_pool.user_pool_id)
        cognito.CfnUserPoolGroup(self, "UsersGroup",  group_name="user",  user_pool_id=user_pool.user_pool_id)

        authorizer = apigw.CognitoUserPoolsAuthorizer(self, "UserAuthorizer", cognito_user_pools=[user_pool])
        auth_opts = apigw.MethodOptions(
            authorizer=authorizer,
            authorization_type=apigw.AuthorizationType.COGNITO
        )


        # Lambda function setup
        def mk_lambda(id_, path, env):
            return _lambda.Function(
                self, id_,
                runtime=_lambda.Runtime.PYTHON_3_11,
                handler="lambda_function.lambda_handler",
                code=_lambda.Code.from_asset(path),
                environment=env,
                timeout=Duration.seconds(10),
                memory_size=256
            )
        env = {
            "BUCKET_NAME": db.content_bucket.bucket_name,
            "ARTISTS_TABLE": db.artists.table_name,
            "ALBUMS_TABLE": db.albums.table_name,
            "TRACKS_TABLE": db.tracks.table_name,
            "TRACK_ARTISTS_TABLE": db.track_artists.table_name,
            "TRACK_GENRES_TABLE": db.track_genres.table_name,
            "GENRES_TABLE": db.genres.table_name,
            "USERS_TABLE": db.users.table_name,
            "PLAYLISTS_TABLE": db.playlists.table_name,
            "PLAYLIST_ITEMS_TABLE": db.playlist_items.table_name,
            "RATINGS_TABLE": db.ratings.table_name,
            "QUEUE_URL": queue.queue_url,
        }

        # artists
        artists_create = mk_lambda("ArtistsCreate", "services/music_service/artists/create", env)
        artists_list   = mk_lambda("ArtistsList",   "services/music_service/artists/list",   env)
        artists_get    = mk_lambda("ArtistsGet",    "services/music_service/artists/get",    env)
        artists_update = mk_lambda("ArtistsUpdate", "services/music_service/artists/update", env)
        artists_delete = mk_lambda("ArtistsDelete", "services/music_service/artists/delete", env)

        # albums
        albums_create  = mk_lambda("AlbumsCreate",  "services/music_service/albums/create",  env)
        albums_list    = mk_lambda("AlbumsList",    "services/music_service/albums/list",    env)
        albums_get     = mk_lambda("AlbumsGet",     "services/music_service/albums/get",     env)
        albums_cov_init_fn = mk_lambda("AlbumsCovInit", "services/music_service/albums/init_cover_upload", env)
        albums_cov_done_fn = mk_lambda("AlbumsCovDone", "services/music_service/albums/complete_cover",    env)
        albums_update  = mk_lambda("AlbumsUpdate",  "services/music_service/albums/update",  env)
        albums_delete  = mk_lambda("AlbumsDelete",  "services/music_service/albums/delete",  env)

        # content (tracks)
        content_init   = mk_lambda("ContentInit",   "services/music_service/content/init_upload", env)
        content_done   = mk_lambda("ContentDone",   "services/music_service/content/complete_upload", env)
        content_list   = mk_lambda("ContentList",   "services/music_service/content/list", env)
        content_get    = mk_lambda("ContentGet",    "services/music_service/content/get",  env)
        track_cov_init_fn = mk_lambda("TrackCovInit",  "services/music_service/content/init_cover_upload", env)
        track_cov_done_fn = mk_lambda("TrackCovDone",  "services/music_service/content/complete_cover",    env)
        content_update = mk_lambda("ContentUpdate", "services/music_service/content/update", env)
        content_delete = mk_lambda("ContentDelete", "services/music_service/content/delete", env)

        # genres
        genres_create = mk_lambda("GenresCreate", "services/music_service/genres/create", env)
        genres_list   = mk_lambda("GenresList",   "services/music_service/genres/list",   env)
        genres_get    = mk_lambda("GenresGet",    "services/music_service/genres/get",    env)
        genres_update = mk_lambda("GenresUpdate", "services/music_service/genres/update", env)
        genres_delete = mk_lambda("GenresDelete", "services/music_service/genres/delete", env)

        # playlists
        playlists_create       = mk_lambda("PlaylistsCreate",       "services/music_service/playlists/create",        env)
        playlists_list_mine    = mk_lambda("PlaylistsListMine",     "services/music_service/playlists/list_mine",     env)
        playlists_get          = mk_lambda("PlaylistsGet",          "services/music_service/playlists/get",           env)
        playlists_update       = mk_lambda("PlaylistsUpdate",       "services/music_service/playlists/update",        env)
        playlists_delete       = mk_lambda("PlaylistsDelete",       "services/music_service/playlists/delete",        env)
        playlists_add_track    = mk_lambda("PlaylistsAddTrack",     "services/music_service/playlists/add_track",     env)
        playlists_remove_track = mk_lambda("PlaylistsRemoveTrack",  "services/music_service/playlists/remove_track",  env)


        # ratings
        ratings_put    = mk_lambda("RatingsPut",    "services/music_service/ratings/put",    env)
        ratings_delete = mk_lambda("RatingsDelete", "services/music_service/ratings/delete", env)

        # SQS consumer to aggregate rating counters on Tracks
        ratings_processor = LambdaWithSqs(
            self, "RatingsProcessor",
            queue=queue,
            handler_path="services/music_service/ratings/processor",
            env=env
        )


        # Permissions
        all_fns = [
            artists_create, artists_list, artists_get, artists_update, artists_delete,
            albums_create, albums_list, albums_get, albums_cov_init_fn, albums_cov_done_fn, albums_update, albums_delete,
            content_init, content_done, content_list, content_get, content_update, content_delete,
            track_cov_init_fn, track_cov_done_fn,
            genres_create, genres_list, genres_get, genres_update, genres_delete,
            playlists_create, playlists_list_mine, playlists_get, playlists_update, playlists_delete,
            playlists_add_track, playlists_remove_track,
            ratings_put, ratings_delete,
            ratings_processor.lambda_function
        ]

        for fn in all_fns:
            db.artists.grant_read_write_data(fn)
            db.albums.grant_read_write_data(fn)
            db.tracks.grant_read_write_data(fn)
            db.track_artists.grant_read_write_data(fn)
            db.track_genres.grant_read_write_data(fn)
            db.genres.grant_read_write_data(fn)
            db.users.grant_read_write_data(fn)
            db.playlists.grant_read_write_data(fn)
            db.playlist_items.grant_read_write_data(fn)
            db.ratings.grant_read_write_data(fn)
            db.content_bucket.grant_read_write(fn)

        queue.grant_send_messages(ratings_put)
        queue.grant_send_messages(ratings_delete)
        queue.grant_consume_messages(ratings_processor.lambda_function)


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

        # API Gateway
        api = apigw.RestApi(
            self, "DemoApi",
            endpoint_configuration=apigw.EndpointConfiguration(
                types=[apigw.EndpointType.REGIONAL]
            )
        )


        # routes
        
        # artists
        artists = api.root.add_resource("artists")
        artists.add_method("POST",  apigw.LambdaIntegration(artists_create), options=auth_opts)
        artists.add_method("GET",   apigw.LambdaIntegration(artists_list),   options=auth_opts)
        artist_id = artists.add_resource("{id}")
        artist_id.add_method("GET",    apigw.LambdaIntegration(artists_get),    options=auth_opts)
        artist_id.add_method("PATCH",  apigw.LambdaIntegration(artists_update), options=auth_opts)
        artist_id.add_method("DELETE", apigw.LambdaIntegration(artists_delete), options=auth_opts)

        # albums
        albums = api.root.add_resource("albums")
        albums.add_method("POST", apigw.LambdaIntegration(albums_create), options=auth_opts)
        albums.add_method("GET",  apigw.LambdaIntegration(albums_list),   options=auth_opts)
        album_id = albums.add_resource("{id}")
        album_id.add_method("GET",    apigw.LambdaIntegration(albums_get),    options=auth_opts)
        album_id.add_method("PATCH",  apigw.LambdaIntegration(albums_update), options=auth_opts)
        album_id.add_method("DELETE", apigw.LambdaIntegration(albums_delete), options=auth_opts)
        albums_cov = albums.add_resource("init-cover-upload")
        albums_cov.add_method("POST", apigw.LambdaIntegration(albums_cov_init_fn), options=auth_opts)
        albums_cov_done = albums.add_resource("complete-cover")
        albums_cov_done.add_method("POST", apigw.LambdaIntegration(albums_cov_done_fn), options=auth_opts)


        # content (tracks)
        content = api.root.add_resource("content")
        init     = content.add_resource("init-upload")
        complete = content.add_resource("complete-upload")
        init.add_method("POST",     apigw.LambdaIntegration(content_init), options=auth_opts)
        complete.add_method("POST", apigw.LambdaIntegration(content_done), options=auth_opts)
        content.add_method("GET",   apigw.LambdaIntegration(content_list), options=auth_opts)
        content_id = content.add_resource("{id}")
        content_id.add_method("GET",    apigw.LambdaIntegration(content_get),    options=auth_opts)
        content_id.add_method("PATCH",  apigw.LambdaIntegration(content_update), options=auth_opts)
        content_id.add_method("DELETE", apigw.LambdaIntegration(content_delete), options=auth_opts)
        track_cov = content.add_resource("init-cover-upload")
        track_cov.add_method("POST", apigw.LambdaIntegration(track_cov_init_fn), options=auth_opts)
        track_cov_done_res = content.add_resource("complete-cover")
        track_cov_done_res.add_method("POST", apigw.LambdaIntegration(track_cov_done_fn), options=auth_opts)

        # genres
        genres = api.root.add_resource("genres")
        genres.add_method("POST", apigw.LambdaIntegration(genres_create), options=auth_opts)
        genres.add_method("GET",  apigw.LambdaIntegration(genres_list),   options=auth_opts)
        genre_id = genres.add_resource("{id}")
        genre_id.add_method("GET",    apigw.LambdaIntegration(genres_get),    options=auth_opts)
        genre_id.add_method("PATCH",  apigw.LambdaIntegration(genres_update), options=auth_opts)
        genre_id.add_method("DELETE", apigw.LambdaIntegration(genres_delete), options=auth_opts)
        
        # playlists
        playlists = api.root.add_resource("playlists")
        playlists.add_method("POST", apigw.LambdaIntegration(playlists_create), options=auth_opts)
        playlists.add_method("GET",  apigw.LambdaIntegration(playlists_list_mine), options=auth_opts)
        pl_id = playlists.add_resource("{id}")
        pl_id.add_method("GET",    apigw.LambdaIntegration(playlists_get),    options=auth_opts)
        pl_id.add_method("PATCH",  apigw.LambdaIntegration(playlists_update), options=auth_opts)
        pl_id.add_method("DELETE", apigw.LambdaIntegration(playlists_delete), options=auth_opts)
        pl_tracks = pl_id.add_resource("tracks")
        pl_tracks.add_method("POST", apigw.LambdaIntegration(playlists_add_track), options=auth_opts)
        pl_trk_id = pl_tracks.add_resource("{trackId}")
        pl_trk_id.add_method("DELETE", apigw.LambdaIntegration(playlists_remove_track), options=auth_opts)

        # ratings
        rating = content_id.add_resource("rating")
        rating.add_method("PUT",    apigw.LambdaIntegration(ratings_put),    options=auth_opts)
        rating.add_method("DELETE", apigw.LambdaIntegration(ratings_delete), options=auth_opts)



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
