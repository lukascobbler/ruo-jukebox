## osobine setupa:

```
lambde samo upisuju i citaju iz dinamoDB - streamovi hendluju triggerovanje
asinhronost kroz streamove u tabelama - obrada kroz batcheve
streamovi daju opciju postavljanja batch_size i max_batching_window
takodje kod streamova ima pracenje "mrtvih" rekorda, splitovanje i pokusaj ponovo, pracenje losih u batchevima i retry
razliciti workeri za razlicite eventove - odvojeno skaliranje (puno reviewova nece ubiti notifikacije)
pay_per_request - TODO da opet ne bankrotiramo
indeksi:
artists.byName(name_lc -> created_at) - pretraga
albums.byArtist(primary_artist_id -> created_at) - prikaz albuma izabranog artista
songs.byAlbum(album_id -> song_no) - pesme albuma po odgovarajucem redosledu
playlists.byOwner(owner_user_id -> created_at) - plejliste usera
playlistItems - sortirane po pozicijama za uredjen prikaz (+ trik sa razmacima od 10)
ratings.byUser(user_id -> content_key) - rejtinzi usera
songArtists.byArtist(artist_id -> song_id) - pesme datog artista
contentGenres.byEntity(entity -> genre) - svi zanrovi za content i obrnuto preko PK
---
ttl za feed i interakcije, aws sam brise
rupe u plejlistama
new_image za interakcije i subskripcije, new i old za ostale
grupe u cognitu za admin control autorizaciju
cognito autorizer za autentifikaciju za lambde
async workeri
dlq za streamove
samo neuspeli u batchevima kod streamova probaju ponovo
====================================================================
upload fajlova kroz dva requesta: TODO mozda bolje 1
ne idu veliki fajlovi kroz lambde i API gateway nego se u prvom koraku salju metapodaci bez bloba, a lambda odgovara sa presigned putom. FE zatim to koristi da se direktno obrati S3 bucketu i dodaje pesmu/sliku, kad uspesno odradi onda salje potvrdu na server (TODO videti kako postici da bude transakcija).
Presigned get se koristi kod streamovanja, gde umesto da ide stream kroz api gateway/lambdu, FE pita za presigned get za streamovanje pesme direktno od strane S3 bucketa i zatim streamuje
```
