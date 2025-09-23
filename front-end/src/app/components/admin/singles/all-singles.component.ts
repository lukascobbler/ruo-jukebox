import {Component, inject} from '@angular/core';
import {
  BoxMissingIconSmallComponent
} from '../../common/missing-icons/box/missing-icon-small/box-missing-icon-small.component';
import {
  MatCell,
  MatCellDef,
  MatColumnDef,
  MatHeaderCell, MatHeaderCellDef,
  MatHeaderRow,
  MatHeaderRowDef,
  MatRow, MatRowDef, MatTable
} from '@angular/material/table';
import {MatIconButton} from '@angular/material/button';
import {Router} from '@angular/router';
import {Song} from '../../../models/Song';

@Component({
  selector: 'app-all-singles',
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
    MatHeaderCellDef
  ],
  templateUrl: './all-singles.component.html',
  styleUrl: './all-singles.component.scss'
})
export class AllSinglesComponent {
  router = inject(Router);

  displayedColumns = ['cover', 'name', 'artist', 'genres', 'actions'];

  singlesDataSource: Song[] = [
    { id: '1', no: 1, title: 'Title', album: 'Album', albumId: '1', duration: 420, artist: 'Awesome Artist 123', artistId: '1', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '2', no: 1, title: 'Title', album: 'Album', albumId: '2', duration: 420, artist: 'Awesome Artist 123', artistId: '2', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '3', no: 1, title: 'Title', album: 'Album', albumId: '3', duration: 420, artist: 'Awesome Artist 123', artistId: '3', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '4', no: 1, title: 'Title', album: 'Album', albumId: '4', duration: 420, artist: 'Awesome Artist 123', artistId: '4', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '5', no: 1, title: 'Title', album: 'Album', albumId: '5', duration: 420, artist: 'Awesome Artist 123', artistId: '5', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '6', no: 1, title: 'Title', album: 'Album', albumId: '6', duration: 420, artist: 'Awesome Artist 123', artistId: '6', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '7', no: 1, title: 'Title', album: 'Album', albumId: '7', duration: 420, artist: 'Awesome Artist 123', artistId: '7', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '8', no: 1, title: 'Title', album: 'Album', albumId: '8', duration: 420, artist: 'Awesome Artist 123', artistId: '8', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '9', no: 1, title: 'Title', album: 'Album', albumId: '9', duration: 420, artist: 'Awesome Artist 123', artistId: '9', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '10', no: 1, title: 'Title', album: 'Album', albumId: '10', duration: 420, artist: 'Awesome Artist 123', artistId: '10', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '11', no: 1, title: 'Title', album: 'Album', albumId: '11', duration: 420, artist: 'Awesome Artist 123', artistId: '11', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '12', no: 1, title: 'Title', album: 'Album', albumId: '12', duration: 420, artist: 'Awesome Artist 123', artistId: '12', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '13', no: 1, title: 'Title', album: 'Album', albumId: '13', duration: 420, artist: 'Awesome Artist 123', artistId: '13', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '14', no: 1, title: 'Title', album: 'Album', albumId: '14', duration: 420, artist: 'Awesome Artist 123', artistId: '14', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '15', no: 1, title: 'Title', album: 'Album', albumId: '15', duration: 420, artist: 'Awesome Artist 123', artistId: '15', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '16', no: 1, title: 'Title', album: 'Album', albumId: '16', duration: 420, artist: 'Awesome Artist 123', artistId: '16', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '17', no: 1, title: 'Title', album: 'Album', albumId: '17', duration: 420, artist: 'Awesome Artist 123', artistId: '17', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '18', no: 1, title: 'Title', album: 'Album', albumId: '18', duration: 420, artist: 'Awesome Artist 123', artistId: '18', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
    { id: '19', no: 1, title: 'Title', album: 'Album', albumId: '19', duration: 420, artist: 'Awesome Artist 123', artistId: '19', lyrics: 'No lyrics found', genres: [{id: '1', name: 'rock'}, {id: '1', name: 'jazz'}, {id: '1', name: 'conutry'}] },
  ];
}
