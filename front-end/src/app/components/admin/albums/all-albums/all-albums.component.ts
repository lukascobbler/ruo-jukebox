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
import {MatDialog, MatDialogRef} from '@angular/material/dialog';
import {CreateAlbumDialogComponent} from '../../dialogs/album/create-album-dialog.component';
import {Artist} from '../../../../models/Artist';
import { GenresService } from '../../../../services/genres/genres.service';

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
  constructor(private genres: GenresService) {}
  dialog = inject(MatDialog);
  router = inject(Router);

  displayedColumns = ['cover', 'name', 'artist', 'genres', 'actions'];
  albumsDataSource: Album[] = [
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}]},
  ];

  getAlbumGenres(album: Album) {
    return album.genres.map(g => g['name']).join(', ');
  }
  create() {
    this.genres.create('Rock').subscribe({
      next: res => console.log('Created genre:', res),
      error: err => console.error('Create failed:', err)
    });
  }

  createNewAlbum() {
    this.create();
    const dialogRef: MatDialogRef<CreateAlbumDialogComponent, null> = this.dialog.open(CreateAlbumDialogComponent, {
      width: '250px',
      minWidth: '22vw'
    });
  }
}
