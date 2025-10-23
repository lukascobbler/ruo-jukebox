import {Component, inject, OnInit} from '@angular/core';
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
import {MatDialog, MatDialogRef} from '@angular/material/dialog';
import {CreateAlbumSongDialogComponent} from '../../dialogs/album-song/create-album-song-dialog.component';
import {NgIf} from '@angular/common';
import {AlbumsService, OfflineAlbumRequest, OfflineSongRequest} from '../../../../services/albums/albums.service';
import {ToastrService} from '../../../../services/toastr/toastr.service';
import {Router} from '@angular/router';
import {lastValueFrom} from 'rxjs';
import {MatProgressSpinner} from '@angular/material/progress-spinner';

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
    NgIf,
    MatProgressSpinner
  ],
  templateUrl: './album-details.component.html',
  styleUrl: './album-details.component.scss'
})
export class AlbumDetailsComponent implements OnInit {
  dialog = inject(MatDialog);
  router = inject(Router);
  albumsService = inject(AlbumsService);
  toastrService = inject(ToastrService);

  loading = true;
  // @ts-ignore
  offlineAlbumRequest: OfflineAlbumRequest;
  displayedColumns = ['name', 'artist', 'genres', 'actions'];

  songsToBeCreated: OfflineSongRequest[] = [];
  numberOfCurrentSongs = 0;

  ngOnInit(): void {
    const state = history.state;
    if (state && state['data']) {
      this.offlineAlbumRequest = state['data'];
      this.loading = false;
    } else {
      this.router.navigate(['all-albums']);
    }
  }

  addSong() {
    const dialogRef: MatDialogRef<CreateAlbumSongDialogComponent, OfflineSongRequest> = this.dialog.open(CreateAlbumSongDialogComponent, {
      minWidth: '900px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.songsToBeCreated = [...this.songsToBeCreated, result];
        this.numberOfCurrentSongs += 1;
      }
    });
  }

  removeSong(offlineSongRequest: OfflineSongRequest) {
    this.numberOfCurrentSongs -= 1;

    const index = this.songsToBeCreated.indexOf(offlineSongRequest);
    if (index > -1) {
      this.songsToBeCreated.splice(index, 1);
    }
  }

  async release() {
    this.loading = true;

    try {
      const initRes = await lastValueFrom(
        this.albumsService.initUpload({
          cover: Boolean(this.offlineAlbumRequest!.coverFile), numberOfSongs: this.numberOfCurrentSongs
        })
      );

      if (this.offlineAlbumRequest!.coverFile && initRes.cover_url)
        await fetch(initRes.cover_url, {method: 'PUT', body: this.offlineAlbumRequest!.coverFile});

      let songUploadCounter = 0;
      for (let songOfflineRequest of this.songsToBeCreated) {
        const { song_id: predefined_song_id, audio_url: predefined_audio_url } = initRes.songs[songUploadCounter];
        await fetch(predefined_audio_url, {method: 'PUT', body: songOfflineRequest.audioFile});
        songOfflineRequest.song_id = predefined_song_id;
        songUploadCounter += 1;
      }

      await lastValueFrom(this.albumsService.completeUpload({
        name: this.offlineAlbumRequest.name,
        album_id: initRes.album_id,
        songs: this.songsToBeCreated.map(tbc => { return {
          song_id: tbc.song_id!, name: tbc.name, genres: tbc.selectedGenres, artists: tbc.selectedArtists }
        }),
        artists: this.offlineAlbumRequest.selectedArtists,
        genres: this.offlineAlbumRequest.selectedGenres,
      }));

      this.toastrService.success('Success', 'Album successfully created');
    } catch {
      this.toastrService.error('Error', 'Unable to upload the album');
    } finally {
      this.loading = false;
      this.router.navigate(['all-albums']);
    }
  }
}
