import {Component, inject, Input, OnInit} from '@angular/core';
import {AsyncPipe, NgClass, NgIf} from '@angular/common';
import {
  MatCell, MatCellDef,
  MatColumnDef,
  MatHeaderCell,
  MatHeaderCellDef,
  MatHeaderRow, MatHeaderRowDef,
  MatRow, MatRowDef,
  MatTable
} from '@angular/material/table';
import {MatIconButton} from '@angular/material/button';
import {Song} from '../../../models/Song';
import {MatDialog, MatDialogRef} from '@angular/material/dialog';
import {AddToPlaylistDialogComponent} from '../dialogs/add-to-playlist/add-to-playlist-dialog.component';
import {Router} from '@angular/router';
import {Artist} from '../../../models/Artist';
import {PlayerService} from '../../../services/player/player.service';
import { SongCacheService } from '../../../services/song-cache/song-cache.service';
import { async, BehaviorSubject } from 'rxjs';

@Component({
  selector: 'app-song-table',
  standalone: true,
  imports: [
    MatTable,
    MatHeaderCell,
    MatColumnDef,
    MatCell,
    MatHeaderCellDef,
    MatRow,
    MatHeaderRow,
    MatHeaderRowDef,
    MatRowDef,
    MatCellDef,
    MatIconButton,
    NgIf,
    NgClass,
    AsyncPipe
  ],
  templateUrl: './song-table.component.html',
  styleUrl: './song-table.component.scss'
})
export class SongTableComponent implements OnInit {
  router = inject(Router);
  player = inject(PlayerService);
  songCache = inject(SongCacheService)

  @Input() songs: Song[] = [];
  @Input() showNumber = true;
  @Input() showAlbum = true;

  displayedColumns: string[] = [];
  cachedSongs = new BehaviorSubject<Set<string>>(new Set());

  constructor(private dialog: MatDialog) {
  }

  ngOnInit(): void {
    if (this.showNumber) {
      this.displayedColumns.push('no');
    }
    this.displayedColumns.push('title');

    if (this.showAlbum) {
      this.displayedColumns.push('album');
    }

    this.displayedColumns.push('duration');
    this.displayedColumns.push('actions');
    this.checkCachedStatus();

  }
  private checkCachedStatus(): void {
    this.songs.forEach(song => {
      this.songCache.isCached(song.content_id).subscribe(isCached => {
        if (isCached) {
          const current = this.cachedSongs.value;
          current.add(song.content_id);
          this.cachedSongs.next(current);
        }
      });
    });
  }

  addToPlaylist(song: Song) {
    const dialogRef: MatDialogRef<AddToPlaylistDialogComponent, null> = this.dialog.open(AddToPlaylistDialogComponent, {
      width: '30rem'
    });
  }

  formatDuration(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  }

  playSong(song: Song) {
    console.log(song)
    this.player.loadPlaylist(this.songs)
    this.player.play(song);
  }
  downloadSongFile(song: Song) {
    this.songCache.downloadCachedSong(song.content_id, song.name).subscribe({
      next: () => console.log('Download started'),
      error: () => {
        fetch(song.audio_url)
          .then(res => res.blob())
          .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${song.name}.mp3`;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
          })
          .catch(err => console.error('Download failed', err));
      }
    });
  }
  cacheForOffline(song: Song) {
    console.log('Caching song:', song);
    this.songCache.cacheSong(song.content_id, song.audio_url).subscribe({
      next: () => {
        console.log('Cached for offline:', song.content_id);
        // Update cached status
        const current = this.cachedSongs.value;
        current.add(song.content_id);
        this.cachedSongs.next(current);
      },
      error: (e) => console.error('Failed to cache song', e),
    });
  }
  protected readonly parseInt = parseInt;
  isCached(song: Song): boolean {
    return this.cachedSongs.value.has(song.content_id);
  }
}
