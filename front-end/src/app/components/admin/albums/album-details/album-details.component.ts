import {Component, inject} from '@angular/core';
import {
  BoxMissingIconSmallComponent
} from "../../../common/missing-icons/box/missing-icon-small/box-missing-icon-small.component";
import {
  MatCell,
  MatCellDef,
  MatColumnDef,
  MatHeaderCell, MatHeaderCellDef,
  MatHeaderRow,
  MatHeaderRowDef,
  MatRow, MatRowDef, MatTable
} from "@angular/material/table";
import {MatIconButton} from "@angular/material/button";
import {Album} from '../../../../models/album/Album';
import {Song} from '../../../../models/Song';
import {MatDialog, MatDialogRef} from '@angular/material/dialog';
import {CreateAlbumDialogComponent} from '../../dialogs/album/create-album-dialog.component';
import {CreateAlbumSongDialogComponent} from '../../dialogs/song/create-album-song-dialog.component';
import {Artist} from '../../../../models/Artist';
import {NgIf} from '@angular/common';
import {AlbumsService} from '../../../../services/albums/albums.service';
import {ToastrService} from '../../../../services/toastr/toastr.service';
import {SongsService} from '../../../../services/singles/singles.service';

@Component({
  selector: 'app-album-details',
  standalone: true,
  imports: [
    BoxMissingIconSmallComponent,
    MatCell,
    MatCellDef,
    MatColumnDef,
    MatHeaderCell,
    MatHeaderRow,
    MatHeaderRowDef,
    MatIconButton,
    MatRow,
    MatRowDef,
    MatTable,
    MatHeaderCellDef,
    NgIf
  ],
  templateUrl: './album-details.component.html',
  styleUrl: './album-details.component.scss'
})
export class AlbumDetailsComponent {
  dialog = inject(MatDialog);
  albumsService = inject(AlbumsService);
  toastrService = inject(ToastrService);
  songsService = inject(SongsService);

  loading = true;
  displayedColumns = ['name', 'artist', 'genres', 'actions'];

  album: Album = {
    id: '1',
    name: 'Awesome album',
    artist: 'Awesome artist',
    artistId: '1',
    released: false,
    genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}],
    songs: [
      {cover_url: '', audio_url: '', song_id: '1', no: 1, name: 'Title', album: 'Album', albumId: '1', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '1', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '2', no: 1, name: 'Title', album: 'Album', albumId: '2', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '2', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '3', no: 1, name: 'Title', album: 'Album', albumId: '3', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '3', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '4', no: 1, name: 'Title', album: 'Album', albumId: '4', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '4', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '5', no: 1, name: 'Title', album: 'Album', albumId: '5', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '5', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '6', no: 1, name: 'Title', album: 'Album', albumId: '6', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '6', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '7', no: 1, name: 'Title', album: 'Album', albumId: '7', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '7', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '8', no: 1, name: 'Title', album: 'Album', albumId: '8', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '8', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '9', no: 1, name: 'Title', album: 'Album', albumId: '9', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '9', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '10', no: 1, name: 'Title', album: 'Album', albumId: '10', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '10', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '11', no: 1, name: 'Title', album: 'Album', albumId: '11', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '11', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '12', no: 1, name: 'Title', album: 'Album', albumId: '12', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '12', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '13', no: 1, name: 'Title', album: 'Album', albumId: '13', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '13', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '14', no: 1, name: 'Title', album: 'Album', albumId: '14', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '14', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '15', no: 1, name: 'Title', album: 'Album', albumId: '15', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '15', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '16', no: 1, name: 'Title', album: 'Album', albumId: '16', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '16', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '17', no: 1, name: 'Title', album: 'Album', albumId: '17', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '17', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '18', no: 1, name: 'Title', album: 'Album', albumId: '18', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '18', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
      {cover_url: '', audio_url: '', song_id: '19', no: 1, name: 'Title', album: 'Album', albumId: '19', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '19', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}]},
    ]
  }

  private loadAlbumSongs(): void {
    this.loading = true;
    // todo
  }

  getSongGenres(song: Song) {
    return song.genres.map(g => g['name']).join(', ');
  }

  releaseAlbum() {
    this.loading = true;
    this.albumsService.release(this.album.id).subscribe({
      next: value => {
        this.album.released = true;
        this.toastrService.success("Successful", "Successfully released the album");
        this.loading = false;
      },
      error: err => {
        this.toastrService.error("Error", "Error releasing the album");
        this.loading = false;
      }
    })
  }

  createNewSong() {
    const dialogRef: MatDialogRef<CreateAlbumSongDialogComponent, null> = this.dialog.open(CreateAlbumSongDialogComponent, {
      width: '250px',
      minWidth: '22vw'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadAlbumSongs();
        this.toastrService.success('Success', 'Song successfully created!');
      }
    });
  }
}
