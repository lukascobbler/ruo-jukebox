Tables:

artists - pk: artist_id
        - attributes: name, bio, genres(string[]), created_at, updated_at
albums - pk: album_id
       - attributes: name, genres(string[]), cover_key(S3 key), created_at
tracks - pk: track_id
       - attributes: title, album_id, file_name, file_type, file_size, file_created_time, file_modified_time, audio_key(S3 key), cover_key(S3 key), created_at
       - GSI: GSI1 - pk = album_id, sk = created_at
TrackArtists - pk: track_id, sk: artist_id
             - GSI byArtist: PK = artist_id, SK=track_id

TrackGenres - pk: genre, sk: track_id