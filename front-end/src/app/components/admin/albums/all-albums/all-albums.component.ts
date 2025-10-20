import {Component, inject, OnInit} from '@angular/core';
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
import {Album} from '../../../../models/album/Album';
import {Router} from '@angular/router';
import {MatDialog, MatDialogRef} from '@angular/material/dialog';
import {AlbumDialogData, CreateAlbumDialogComponent} from '../../dialogs/album/create-album-dialog.component';
import {Artist} from '../../../../models/Artist';
import { GenresService } from '../../../../services/genres/genres.service';
import {AlbumsService} from '../../../../services/albums/albums.service';
import {GenreItem} from '../../../../models/GenreItem';
import {ToastrService} from '../../../../services/toastr/toastr.service';
import {NgIf} from '@angular/common';
import {MatProgressSpinner} from '@angular/material/progress-spinner';

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
    BoxMissingIconSmallComponent,
    NgIf,
    MatProgressSpinner
  ],
  templateUrl: './all-albums.component.html',
  styleUrl: './all-albums.component.scss'
})
export class AllAlbumsComponent implements OnInit {
  dialog = inject(MatDialog);
  router = inject(Router);
  albumsService = inject(AlbumsService);
  toastr = inject(ToastrService);
  loading = true;

  displayedColumns = ['cover', 'name', 'artist', 'genres', 'actions'];
  albumsDataSource: Album[] = [];

  ngOnInit() {
    this.albumsService.list().subscribe({
      next: value => {
        this.albumsDataSource = value;
        this.loading = false;
      },
      error: err => {
        this.toastr.error("Error loading", "Error loading albums: ", err);
        this.loading = false;
      }
    })
  }

  getAlbumGenres(album: Album) {
    return album.genres.map(g => g.name).join(', ');
  }

  createNewAlbum() {
    const dialogRef: MatDialogRef<CreateAlbumDialogComponent, AlbumDialogData | null | undefined> =
      this.dialog.open(CreateAlbumDialogComponent, {
        width: '400px',
        minWidth: '22vw',
      });

    dialogRef.afterClosed().subscribe((result) => {
      if (!result) return;

      const { name } = result;

      const artistId = 'artist1';
      const artistName = 'Awesome artist 1';
      const genreIds = ['rock'];
      const genreObjects: GenreItem[] = [{ id: 'rock', name: 'Rock' }];

      this.albumsService.create({ name, artistId, genreIds })
        .subscribe({
          next: (created) => {
            const newAlbum: Album = {
              id: created.id,
              name: created.name,
              artist: artistName,
              artistId,
              genres: genreObjects,
              released: false
            };
            this.albumsDataSource = [...this.albumsDataSource, newAlbum];
          },
          error: (err) => {
            this.toastr.error('Error','Album creation failed: ', err);
          },
        });
    });
  }
}
