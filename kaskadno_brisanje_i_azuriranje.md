## Kaskadno brisanje i azuriranje

```
Podesiti poseban sqs sa dql i lambda worker za kaskadna brisanja.

Brisanje pesme:
brisanje iz TrackArtists
brisanje iz ContentGenres
birsanje iz PlaylistItems
brisanje iz Ratings
brisanje iz Transcriptions
brisanje same pesme i slike(ako je singl) iz S3 bucketa
brisanje iz Tracks na kraju

Brisanje albuma:
pozovi brisanje za svaku pesmu iz albuma (ovo prethodno) (Tracks.byAlbum)
brisanje iz ContentGenres
brisanje slike iz S3
brisanje iz Albums na kraju

Brisanje artista:
pozovi brisanje za svaki album artista (Albums.byArtist)
pozovi brisanje za svaku pesmu (preostali su singlovi van albuma) (TrackArtists.byArtist, prethodno opisano)
brisanje iz ContentGenres
brisanje slike iz S3
brisanje artista na kraju

brisanje zanra:
ContentGenres PK = genre_id, obrisi sve
brisanje iz Genres na kraju

Od kaskadnih azuriranja ima samo izmena naziva zanra jer mu je naziv id, inace ne treba jer sve ide preko id.

azuriranje naziva zanra: (mozda samo zabraniti, nek brise pa dodaje?)
uzeti sve ContentGenres PK = stari_id, napraviti "kopiju" svih tih sa novi_id
obrisati sve sa stari_id
```
