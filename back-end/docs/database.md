## ContentTable {PK} - {SK}

```
ALBUM~{UUID}  - META
SINGLE~{UUID} - META
ALBUM~{UUID}  - POS~{POS}~SONG~{UUID}
SINGLE~{UUID} - POS~{POS}~SONG~{UUID}
ARTIST~{UUID} - META
ARTIST~{UUID} - CONTENT~SONG~{UUID}
                CONTENT~ALBUM~{UUID}
                CONTENT~SINGLE~{UUID}
GENRE~{UUID}  - META
GENRE~{UUID}  - CONTENT~ARTIST~{UUID}
                CONTENT~SONG~{UUID}
                CONTENT~ALBUM~{UUID}
                CONTENT~SINGLE~{UUID}
```

### GSI byName {PK} - {SK}

```
{name_lc} - {content_type}

content_type  =  ARTIST | ALBUM | SONG
```

### GSI byType {PK} - {SK}

```
{content_type} - <NO_SK>

content_type  =  ARTIST | ALBUM | SINGLE | SONG | GENRE
```

## UserdataTable {PK} - {SK}

```
USER~{UUID} - META
USER~{UUID} - PLAYLIST~{UUID}~CONTENT
USER~{UUID} - PLAYLIST~{UUID}~POS~{POS}~SONG~{UUID}
USER~{UUID} - RATING~SONG~{UUID}
USER~{UUID} - SUB~GENRE~{UUID}
              SUB~ARTIST~{UUID}

user_id  =  {PK}
```

### GSI ratingBySong {PK} - {SK} (used for feed)

```
{song_id} - {rating}

song_id   =  SONG~{UUID}
rating   =  1 | 2 | 3
```

### GSI getSubscribed {PK} - {SK}

```
{sub_id} - <NO_SK>

sub_id  =  SUB~GENRE~{UUID} | SUB~ARTIST~{UUID}
```

## InteractionsTable

```
USER~{UUID} - {ts}

user_id  =  {PK}
ts       =  {SK}
```

## FeedTable

```
USER~{UUID} - ARTIST~{UUID}
              ALBUM~{UUID}
              SONG~{UUID}

user_id     =  {PK}
content_id  =  {SK}
```