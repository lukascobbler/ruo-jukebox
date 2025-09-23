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
      { id: '1', no: 1, title: 'Title', album: 'Album', albumId: '1', duration: 420, artist: 'Awesome Artist 123', artistId: '1' },
      { id: '2', no: 1, title: 'Title', album: 'Album', albumId: '2', duration: 420, artist: 'Awesome Artist 123', artistId: '2' },
      { id: '3', no: 1, title: 'Title', album: 'Album', albumId: '3', duration: 420, artist: 'Awesome Artist 123', artistId: '3' },
      { id: '4', no: 1, title: 'Title', album: 'Album', albumId: '4', duration: 420, artist: 'Awesome Artist 123', artistId: '4' },
      { id: '5', no: 1, title: 'Title', album: 'Album', albumId: '5', duration: 420, artist: 'Awesome Artist 123', artistId: '5' },
      { id: '6', no: 1, title: 'Title', album: 'Album', albumId: '6', duration: 420, artist: 'Awesome Artist 123', artistId: '6' },
      { id: '7', no: 1, title: 'Title', album: 'Album', albumId: '7', duration: 420, artist: 'Awesome Artist 123', artistId: '7' },
      { id: '8', no: 1, title: 'Title', album: 'Album', albumId: '8', duration: 420, artist: 'Awesome Artist 123', artistId: '8' },
      { id: '9', no: 1, title: 'Title', album: 'Album', albumId: '9', duration: 420, artist: 'Awesome Artist 123', artistId: '9' },
      { id: '10', no: 1, title: 'Title', album: 'Album', albumId: '10', duration: 420, artist: 'Awesome Artist 123', artistId: '10' },
      { id: '11', no: 1, title: 'Title', album: 'Album', albumId: '11', duration: 420, artist: 'Awesome Artist 123', artistId: '11' },
      { id: '12', no: 1, title: 'Title', album: 'Album', albumId: '12', duration: 420, artist: 'Awesome Artist 123', artistId: '12' },
      { id: '13', no: 1, title: 'Title', album: 'Album', albumId: '13', duration: 420, artist: 'Awesome Artist 123', artistId: '13' },
      { id: '14', no: 1, title: 'Title', album: 'Album', albumId: '14', duration: 420, artist: 'Awesome Artist 123', artistId: '14' },
      { id: '15', no: 1, title: 'Title', album: 'Album', albumId: '15', duration: 420, artist: 'Awesome Artist 123', artistId: '15' },
      { id: '16', no: 1, title: 'Title', album: 'Album', albumId: '16', duration: 420, artist: 'Awesome Artist 123', artistId: '16' },
      { id: '17', no: 1, title: 'Title', album: 'Album', albumId: '17', duration: 420, artist: 'Awesome Artist 123', artistId: '17' },
      { id: '18', no: 1, title: 'Title', album: 'Album', albumId: '18', duration: 420, artist: 'Awesome Artist 123', artistId: '18' },
      { id: '19', no: 1, title: 'Title', album: 'Album', albumId: '19', duration: 420, artist: 'Awesome Artist 123', artistId: '19' },
      { id: '20', no: 1, title: 'Title', album: 'Album', albumId: '20', duration: 420, artist: 'Awesome Artist 123', artistId: '0' },
    ];
  }

  addToPlaylist(song: Song) {
    const dialogRef: MatDialogRef<AddToPlaylistDialogComponent, null> = this.dialog.open(AddToPlaylistDialogComponent, {
      width: '30rem'
    });
  }
}
