import {Component, Input, OnInit} from '@angular/core';
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
  @Input() recommendedSongsDataSource: Song[] = [];
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

    this.recommendedSongsDataSource = [
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
      { id: '', no: 1, title: 'Title', album: 'Album', albumId: '', duration: 420 },
    ];
  }

  addToPlaylist(song: Song) {
    const dialogRef: MatDialogRef<AddToPlaylistDialogComponent, null> = this.dialog.open(AddToPlaylistDialogComponent, {
      width: '30rem'
    });
  }
}
