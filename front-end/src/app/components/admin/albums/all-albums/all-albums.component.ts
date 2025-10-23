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
import {AlbumsService, OfflineAlbumRequest} from '../../../../services/albums/albums.service';
import {Genre} from '../../../../models/Genre';
import {ToastrService} from '../../../../services/toastr/toastr.service';
import {NgIf} from '@angular/common';
import {MatProgressSpinner} from '@angular/material/progress-spinner';
import {CreateSingleDialogComponent} from '../../dialogs/single/create-single-dialog.component';

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
  toast = inject(ToastrService);
  loading = true;

  displayedColumns = ['cover', 'name', 'artists', 'genres', 'actions'];
  albumsDataSource: Album[] = [];

  ngOnInit() {
    this.loadAlbums();
  }

  getAlbumGenres(album: Album) {
    return album.genres.map(g => g.name).join(', ');
  }

  private loadAlbums(): void {
    this.loading = true;
    this.albumsService.list().subscribe({
      next: (albums) => {
        this.albumsDataSource = albums;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  createNewAlbum() {
    const dialogRef: MatDialogRef<CreateAlbumDialogComponent, OfflineAlbumRequest | null> = this.dialog.open(CreateAlbumDialogComponent, {
      minWidth: '500px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.router.navigate(['album-details'], { state: { data: result } })
      }
    });
  }
}
