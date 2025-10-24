import {Component, inject, Input, OnInit} from '@angular/core';
import {NgClass, NgIf} from '@angular/common';
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
    NgClass
  ],
  templateUrl: './song-table.component.html',
  styleUrl: './song-table.component.scss'
})
export class SongTableComponent implements OnInit {
  router = inject(Router);
  player = inject(PlayerService);

  @Input() songs: Song[] = [];
  @Input() showNumber = true;
  @Input() showAlbum = true;

  displayedColumns: string[] = [];

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

  protected readonly parseInt = parseInt;
}
