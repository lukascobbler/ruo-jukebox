## Kaskadno brisanje i azuriranje

```
Podesiti poseban sqs sa dql i lambda worker za kaskadna brisanja.

Brisanje pesme:
brisanje iz SongArtists
brisanje iz ContentGenres
birsanje iz PlaylistItems
brisanje iz Ratings
brisanje iz Transcriptions
brisanje same pesme i slike(ako je singl) iz S3 bucketa
brisanje iz Songs na kraju

Brisanje albuma:
pozovi brisanje za svaku pesmu iz albuma (ovo prethodno) (Songs.byAlbum)
brisanje iz ContentGenres
brisanje slike iz S3
brisanje iz Albums na kraju

Brisanje artista:
pozovi brisanje za svaki album artista (Albums.byArtist)
pozovi brisanje za svaku pesmu (preostali su singlovi van albuma) (SongArtists.byArtist, prethodno opisano)
brisanje iz ContentGenres
brisanje slike iz S3
brisanje subskripcije na artista
brisanje artista na kraju

brisanje zanra:
brisati sve iz ContentGenres
brisanje iz Genres na kraju

```
