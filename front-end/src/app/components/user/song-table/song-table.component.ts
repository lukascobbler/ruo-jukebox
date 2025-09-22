import {Component, Input, OnInit} from '@angular/core';
import {NgIf} from '@angular/common';
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
    NgIf
  ],
  templateUrl: './song-table.component.html',
  styleUrl: './song-table.component.scss'
})
export class SongTableComponent implements OnInit {
  @Input() recommendedSongsDataSource: Song[] = [];
  @Input() showNumber = true;

  displayedColumns: string[] = [];

  ngOnInit(): void {
    if (this.showNumber) {
      this.displayedColumns = ['no', 'title', 'album', 'duration', 'actions']
    } else {
      this.displayedColumns = ['title', 'album', 'duration', 'actions']
    }

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
    ]
  }
}
