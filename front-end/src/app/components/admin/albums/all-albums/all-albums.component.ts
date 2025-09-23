import {Component, inject} from '@angular/core';
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
import {
  BoxMissingIconSmallComponent
} from '../../../common/missing-icons/box/missing-icon-small/box-missing-icon-small.component';
import {Album} from '../../../../models/Album';
import {Router} from '@angular/router';

@Component({
  selector: 'app-all-albums',
  standalone: true,
  imports: [
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
    BoxMissingIconSmallComponent
  ],
  templateUrl: './all-albums.component.html',
  styleUrl: './all-albums.component.scss'
})
export class AllAlbumsComponent {
  router = inject(Router);

  displayedColumns = ['cover', 'name', 'artist', 'actions'];
  albumsDataSource: Album[] = [
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1'},
  ];
}
