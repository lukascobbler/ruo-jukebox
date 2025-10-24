
1 user - 1 lambda

InteractionsTable
PK = USER~{UUID}


# INTERAKCIJE


[
    {
        "user_id": "USER~{UUID}",
        "ts": 78971379,
        "ttl": 345345673,
        “value”: 1 - 10 - 20 - 30 -50
        "artists": [
            "ARTIST~{UUID}",
            "ARTIST~{UUID}",
            "ARTIST~{UUID}"
        ],
        "genres": [
            "GENRE~{UUID}",
            "GENRE~{UUID}",
            "GENRE~{UUID}"
        ],
        "album_id": "ALBUM~{UUID}",
        "song_id": ""
    },
    {
        "user_id": "USER~{UUID}",
        "ts": 78971379,
        "ttl": 345345673,
        "artists": [
            "ARTIST~{UUID}",
            "ARTIST~{UUID}",
            "ARTIST~{UUID}"
        ],
        "genres": [
            "GENRE~{UUID}",
            "GENRE~{UUID}",
            "GENRE~{UUID}"
        ],
        "album_id": "ALBUM~{UUID}",
        "song_id": ""
    },
    {
        "user_id": "USER~{UUID}",
        "ts": 78971379,
        "ttl": 345345673,
        "artists": [
            "ARTIST~{UUID}",
            "ARTIST~{UUID}",
            "ARTIST~{UUID}"
        ],
        "genres": [
            "GENRE~{UUID}",
            "GENRE~{UUID}",
            "GENRE~{UUID}"
        ],
        "album_id": "ALBUM~{UUID}",
        "song_id": ""
    }
]


# ONO ŠTO VOLI


min_ts
max_ts

rating → 0, 1, 2, 3
get_period(ts) → 1, 2, 3, 4

time_of_day = get_period(ts) == get_period(current_ts) ? 1.5 : 1
fresh = 1 + (ts - min_ts) / (max_ts / min_ts)   # od 1 do 2
liking = 1 + rating

value * fresh * time_of_day * liking


{
    artists_seen: {
        artist_id: count,
        artist_id: count,
        artist_id: count,
        artist_id: count,
        artist_id: count
    },
    genres_seen: {
        artist_id: count,
        artist_id: count,
        artist_id: count,
        artist_id: count,
        artist_id: count
    },
    songs_seen: {
        artist_id: count,
        artist_id: count,
        artist_id: count,
        artist_id: count,
        artist_id: count
    },
    albums_seen: {
        artist_id: count,
        artist_id: count,
        artist_id: count,
        artist_id: count,
        artist_id: count
    }
}

artists_seen = sort(artists_seen)[50:]
genres_seen = sort(genres_seen)[50:]
songs_seen = sort(songs_seen)[50:]
albums_seen = sort(albums_seen)[50:]


# ONO ŠTO BI MU SE SVIDELO (ŠTO JE POVEZANO)


for each of seen query connected from db
artists_seen → albums_not_seen, songs_not_seen
genres_seen → artists_not_seen, albums_not_seen, songs_not_seen
songs_seen → artists_not_seen, albums_not_seen
albums_seen → artists_not_seen, songs_not_seen


mumble jumble of not seen artists, albums, songs 


# DOPUNI SA RANDOM (AKO FALI)

missing_artists = 50 - count(artists_not_seen)
missing_albums = 50 - count(albums_not_seen)
missing_songs = 50 - count(songs_not_seen)

artists_not_seen += query_random_artists[missing_artists:]
albums_not_seen += query_random_albums[missing_albums:]
songs_not_seen += query_random_songs[missing_songs:]



{
    artists_not_seen: [
        artist_id,
        artist_id,
        artist_id,
        artist_id,
        artist_id
    ],
    songs_not_seen:[
        artist_id,
        artist_id,
        artist_id,
        artist_id,
        artist_id
    ],
    albums_not_seen:[
        artist_id,
        artist_id,
        artist_id,
        artist_id,
        artist_id
    ]
}

























# SORTIRAJ PO POPULARNOSTI


for each of not seen artists, albums, songs get
rating_coef = rating_sum / num_of_ratings


{
    artists_not_seen: [
        artist_id: rating_coef,
        artist_id: rating_coef,
        artist_id: rating_coef,
        artist_id: rating_coef,
        artist_id: rating_coef
    ],
    songs_not_seen: {
        artist_id: rating_coef,
        artist_id: rating_coef,
        artist_id: rating_coef,
        artist_id: rating_coef,
        artist_id: rating_coef
    },
    albums_not_seen: {
        artist_id: rating_coef,
        artist_id: rating_coef,
        artist_id: rating_coef,
        artist_id: rating_coef,
        artist_id: rating_coef
    }
}


artists_not_seen = sort(artists_not_seen)
songs_not_seen = sort(songs_not_seen)
albums_not_seen = sort(albums_not_seen)
