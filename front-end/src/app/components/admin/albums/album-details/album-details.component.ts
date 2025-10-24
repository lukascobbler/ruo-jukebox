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
import {BoxMissingIconMediumComponent} from '../../../common/missing-icons/box/missing-icon-medium/box-missing-icon-medium.component';
import {Album} from '../../../../models/Album';
import {Single} from '../../../../models/Single';
import {PlayerService} from '../../../../services/player/player.service';
import {Song} from '../../../../models/Song';

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
  player = inject(PlayerService);

  loading = true;
  offlineAlbumRequest: OfflineAlbumRequest | undefined;
  displayedColumns = ['name', 'artists', 'genres', 'actions'];
  album_id: string | undefined;

  songs: OfflineSongRequest[] = [];
  numberOfCurrentSongs = 0;
  editMode = false;
  albumName?: string;
  cover?: string;

  ngOnInit(): void {
    const state = history.state;

    if (state && state['data']) {
      ({result: this.offlineAlbumRequest, album_id: this.album_id, cover_url: this.cover} = state['data'] || {});

      if (this.offlineAlbumRequest) {
        this.albumName = this.offlineAlbumRequest.name;
        this.editMode = false;
        this.loading = false;
      } else if (this.album_id) {
        this.editMode = true;
        this.albumsService.get(this.album_id).subscribe(album => {
          this.loading = false
          this.albumName = album.name;
          this.songs = album.songs as unknown as OfflineSongRequest[];
        });
      }
    } else {
      this.router.navigate(['all-albums']);
    }

    if (this.offlineAlbumRequest && this.offlineAlbumRequest.coverFile instanceof File)
      this.cover = URL.createObjectURL(this.offlineAlbumRequest.coverFile);
  }

  addSong() {
    const dialogRef: MatDialogRef<CreateAlbumSongDialogComponent, OfflineSongRequest> = this.dialog.open(CreateAlbumSongDialogComponent, {
      minWidth: '450px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.songs = [...this.songs, result];
        this.numberOfCurrentSongs += 1;
      }
    });
  }

  getSongGenres(song: OfflineSongRequest) {
    return song.genres.map(s => s.name).join(', ');
  }

  getSongArtists(song: OfflineSongRequest) {
    return song.artists.map(s => s.name).join(', ');
  }

  removeSong(offlineSongRequest: OfflineSongRequest) {
    this.numberOfCurrentSongs -= 1;

    const index = this.songs.indexOf(offlineSongRequest);
    if (index > -1) {
      this.songs.splice(index, 1);
    }
  }

  async release() {
    if (this.editMode) {
      return;
    }

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
      for (let songOfflineRequest of this.songs) {
        const {song_id: predefined_song_id, audio_url: predefined_audio_url} = initRes.songs[songUploadCounter];
        await fetch(predefined_audio_url, {method: 'PUT', body: songOfflineRequest.audioFile});
        songOfflineRequest.song_id = predefined_song_id;
        songUploadCounter += 1;
      }

      await lastValueFrom(this.albumsService.completeUpload({
        name: this.offlineAlbumRequest!.name,
        album_id: initRes.album_id,
        songs: this.songs.map(tbc => {
          return {
            song_id: tbc.song_id!, name: tbc.name, genres: tbc.selectedGenres, artists: tbc.selectedArtists
          }
        }),
        artists: this.offlineAlbumRequest!.selectedArtists,
        genres: this.offlineAlbumRequest!.selectedGenres,
      }));

      this.loading = false;
      this.router.navigate(['all-albums']);
      this.toastrService.success('Success', 'Album successfully created');
    } catch {
      this.loading = false;
      this.toastrService.error('Error', 'Unable to upload the album');
    }
  }

  playSong(song: Song): void {
    console.log(song);
    this.player.play(song);
  }
}
