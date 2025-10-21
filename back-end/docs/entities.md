## SONG

```python
core_song = {
    "content_id": "SONG~{UUID}",
    "content_type": "SONG",
    "name": "Super song",
    "name_lc": "super song",
    "audio_key": "songs/SONG~{UUID}.mp3",
    "cover_key": "singles/SINGLE~{UUID}.jpg" | "albums/ALBUM~{UUID}.jpg",
    "transcription_key": "transcriptions/SONG~{UUID}.txt",
    "artists": [{
        "artist_id": "ARTIST~{UUID}",
        "name": "Super artist 1"
    }, {
        "artist_id": "ARTIST~{UUID}",
        "name": "Super artist 2"
    }],
    "genres": [{
        "genre_id": "GENRE~{UUID}",
        "name": "Super genre 1"
    }, {
        "genre_id": "GENRE~{UUID}",
        "name": "Super genre 2"
    }]
}

core_table = {
    "PK": "ALBUM~{UUID}" | "SINGLE~{UUID}",
    "SK": "POS~{POS}~SONG~{UUID}",
    **core_song
}

# add this to table for every artist
getArtist = {
    "PK": "ARTIST~{UUID}",
    "SK": "CONTENT~SONG~{UUID}",
    **core_song
}

# add this to table for every genre
getGenre = {
    "PK": "GENRE~{UUID}",
    "SK": "CONTENT~SONG~{UUID}",
    **core_song
}
```

## ALBUM

```python
core_album = {
    "content_id": "ALBUM~{UUID}",
    "content_type": "ALBUM",
    "name": "Super album",
    "name_lc": "super album",
    "cover_key": "albums/ALBUM~{UUID}.jpg",
    "artists": [{
        "artist_id": "ARTIST~{UUID}",
        "name": "Super artist 1"
    }, {
        "artist_id": "ARTIST~{UUID}",
        "name": "Super artist 2"
    }],
    "genres": [{
        "genre_id": "GENRE~{UUID}",
        "name": "Super genre 1"
    }, {
        "genre_id": "GENRE~{UUID}",
        "name": "Super genre 2"
    }]
}

core_table = {
    "PK": "ALBUM~{UUID}",
    "SK": "META",
    **core_album
}

# add this to table for every artist
getArtist = {
    "PK": "ARTIST~{UUID}",
    "SK": "CONTENT~ALBUM~{UUID}",
    **core_album
}

# add this to table for every genre
getGenre = {
    "PK": "GENRE~{UUID}",
    "SK": "CONTENT~ALBUM~{UUID}",
    **core_album
}
```

## SINGLE

```python
core_single = {
    "content_id": "SINGLE~{UUID}",
    "content_type": "SINGLE",
    # same as in song
    "name": "Super song",
    "cover_key": "singles/SINGLE~{UUID}.jpg",
    "artists": [{
        "artist_id": "ARTIST~{UUID}",
        "name": "Super artist 1"
    }, {
        "artist_id": "ARTIST~{UUID}",
        "name": "Super artist 2"
    }],
    "genres": [{
        "genre_id": "GENRE~{UUID}",
        "name": "Super genre 1"
    }, {
        "genre_id": "GENRE~{UUID}",
        "name": "Super genre 2"
    }]
}

core_table = {
    "PK": "SINGLE~{UUID}",
    "SK": "META",
    **core_single
}

# same ARTIST~{UUID} as for song, add this to table for every artist
getArtist = {
    "PK": "ARTIST~{UUID}",
    "SK": "CONTENT~SINGLE~{UUID}",
    **core_single
}

# same GENRE~{UUID} as for song, add this to table for every genre
getGenre = {
    "PK": "GENRE~{UUID}",
    "SK": "CONTENT~SINGLE~{UUID}",
    **core_single
}
```

## ARTIST

```python
core_artist = {
    "artist_id": "ARTIST~{UUID}",
    "content_type": "ARTIST",
    "name": "Super artist",
    "name_lc": "super artist",
    "biography": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "cover_key": "artists/ARTIST~{UUID}.jpg",
    "genres": [{
        "genre_id": "GENRE~{UUID}",
        "name": "Super genre 1"
    }, {
        "genre_id": "GENRE~{UUID}",
        "name": "Super genre 2"
    }]
}

core_table = {
    "PK": "ARTIST~{UUID}",
    "SK": "META",
    **core_artist
}

# add this to table for every genre
getGenre = {
    "PK": "GENRE~{UUID}",
    "SK": "CONTENT~ARTIST~{UUID}",
    **core_artist
}
```

## GENRE

```python
core_genre = {
    "genre_id": "GENRE~{UUID}",
    "content_type": "GENRE",
    "name": "Super genre"
}

core_table = {
    "PK": "GENRE~{UUID}",
    "SK": "META",
    **core_genre
}
```

## USER

```python
user_table = {
    "user_id": "USER~{UUID}",
    "SK": "META",
    "name": "Super name",
    "surname": "Super surname",
    "email": "super@email.com",
    "birthday": "1.1.2000."
}
```

## PLAYLIST

```python
user_table = {
    "user_id": "USER~{UUID}",
    "SK": "PLAYLIST~{UUID}~CONTENT",
    "playlist_id": "PLAYLIST~{UUID}",
    "name": "Super playlist"
}
```

## PLAYLIST_ITEM

```python
user_table = {
    "user_id": "USER~{UUID}",
    "SK": "PLAYLIST~{UUID}~POS~{POS}~SONG~{UUID}",
    "playlist_id": "PLAYLIST~{UUID}"
}

```

## RATING

```python
user_table = {
    "user_id": "USER~{UUID}",
    "SK": "RATING~SONG~{UUID}",
    "song_id": "SONG~{UUID}",
    "rating": "3"
}
```

## SUBSCRIPTION

```python
user_table = {
    "user_id": "USER~{UUID}",
    "SK": "SUB~GENRE~{UUID}" | "SUB~ARTIST~{UUID}",
    "sub_id": "SUB~GENRE~{UUID}" | "SUB~ARTIST~{UUID}"
}
```

## INTERACTION

```python
interactions_table = {
    "user_id": "USER~{UUID}",
    "ts": 78971379,
    "ttl": 345345673,
    "artist_id": "",
    "album_id": "",
    "song_id": ""
}
```

## FEED

```python
feed_table = {
    "user_id": "USER~{UUID}",
    "content_id": "ARTIST~{UUID}" | "ALBUM~{UUID}" | "SONG~{UUID}"
}
```