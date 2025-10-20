## Bucketi:

```
audio_bucket, images_bucket, transcripts_bucket (jedini blobovi)
```

## tabele:

```
artists (byName)
albums (byArtist)
songs (byAlbum - za album trazi pesme u odgovarajucem redosledu)
genres
songArtists(byArtist)
contentGenres(genericno da se veze za artist/song/album) (byEntity)
users(cognito useri)
playlists(byOwner)
playlistsItems(bySong - mozda visak)
ratings(byUser)
subscriptions(byUser)
interactions
feed
transcriptions
```

## primeri podataka u tabelama:

### artist:

```json
{
  "artist_id": "ART_9c42",
  "name": "Alicia Keys",
  "name_lc": "alicia keys",
  "biography": "…",
  "photo_key": "images/artists/ART_9c42.jpg",
  "created_at": 1760701200,
}
```

### album:

```json
{
  "album_id": "ALB_8b11",
  "title": "Midnight Sessions",
  "primary_artist_id": "ART_9c42",
  "photo_key": "images/albums/ALB_8b11.jpg",
  "created_at": 1760703600,
}
```

### song:

```json
{
  "song_id": "SNG_a1f0",
  "title": "Starlight",
  "album_id": "ALB_8b11",             // ako nema album_id znaci da je singl
  "song_no": 2,                      // redosled unutar albuma, isto preskociti ako je singl
  "duration_sec": 241,
  "audio_key": "audio/SNG_a1f0.mp3",
  "created_at": 1760704200,
  "stats": { "rating_sum": 9, "rating_cnt": 4 } // agregator workeri sredjuju
}
```

### genre:

```json
{
  "genre_id": "GNR_1b17",
  "display": "Rock",
  "description": "Guitars, drums…",
  "created_at": 1760690000
}
```

### songArtist:

```json
{
  "song_id": "SNG_a1f0",
  "artist_id": "ART_9c42",
}
```

### contentGenre (generic):

```json
{ "genre": "GNR_1b17", "entity": "ART_9c42", "created_at": 1760701200 }
{ "genre": "GNR_1b17", "entity": "ALB_8b11",  "created_at": 1760703600 }
{ "genre": "GNR_1b17", "entity": "SNG_a1f0",  "created_at": 1760704200 }
```

### user: (cognito za autorizaciju, ovo sluzi za biznis logiku)

```json
{
  "user_id": "SUB_3c0f1a",
  "username": "name",
  "email": "user@example.com",
  "given_name": "FirstName",
  "family_name": "LastName",
  "birthdate": "2003-05-17",
  "created_at": 1760700000
}
```

### playlistItem:

```json
{
  "playlist_id": "PL_7d44",
  "position": 10,               
  "song_id": "SNG_a1f0",
  "added_at": 1760707300
}
```

### rating:

```json
{
  "song_id": "SNG_a1f0",
  "user_id": "SUB_3c0f1a",
  "value": 3,                        // 1..3
  "rated_at": 1760707400
}
```

### subscription (genericno fleksibilno):

```json
{
  "topic": "ARTIST#ART_9c42",      // moze i na GENRE#, mozda visak
  "user_id": "SUB_3c0f1a",
  "since": 1760707500
}
```

### interaction:

```json
{
  "user_id": "SUB_3c0f1a",
  "ts": 1760707601,
  "type": "PLAY",                   // PLAY | RATE | ADD_TO_PLAYLIST | ...
  "song_id": "SNG_a1f0",
  "ms_listened": 241000
}
```

### feed:

```json
{
  "user_id": "SUB_3c0f1a",
  "item_id": "ALB_8b11#1760707900",
  "ts": 1760707900,
  "ttl": 1763319900
}
```

### transkripcije:

```json
{
  "song_id": "SNG_a1f0",
  "status": "READY",          // PENDING | READY | FAILED ovo jos videti jer ima ona fora retry nesto pise na specifikaciji TODO
  "transcript_key": "transcripts/SNG_a1f0.json",
  "updated_at": 1760708000
}
```

---

kod pozicioniranja za albume i plejliste preporucuje se da se koriste gapovi tipa 10, 20, 30 ili 100, 200, 300, pa ako se ubaci u medjuvremenu nesto da bude novi id 15 ili 25 i tako, da ne bi morali svi da se izmestaju redom za jedan, ovo jos pogledati TODO
