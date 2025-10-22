import {Component, Inject, inject, numberAttribute, OnInit, ViewChild} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatIconButton } from '@angular/material/button';
import { MatInput } from '@angular/material/input';
import { MatOption } from '@angular/material/core';
import { MatSelect } from '@angular/material/select';
import { UploadImageBoxComponent } from '../upload-image-box/upload-image-box.component';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {NgForOf, NgIf} from '@angular/common';
import {lastValueFrom} from 'rxjs';
import {AlbumsService, OfflineAlbumRequest} from '../../../../services/albums/albums.service';
import {ToastrService} from '../../../../services/toastr/toastr.service';
import {MatProgressSpinner} from '@angular/material/progress-spinner';
import {GenresService} from '../../../../services/genres/genres.service';
import {ArtistsService} from '../../../../services/artists/artists.service';
import {Artist} from '../../../../models/Artist';

export interface AlbumDialogData {
  name: string;
  artistId: string;
  genreIds: string[];
  pictureFile?: File;
}

@Component({
  selector: 'app-create-album-dialog',
  standalone: true,
  imports: [
    FormsModule,
    MatFormField,
    MatIconButton,
    MatInput,
    MatLabel,
    MatOption,
    MatSelect,
    UploadImageBoxComponent,
    NgForOf,
    MatProgressSpinner,
    NgIf
  ],
  templateUrl: './create-album-dialog.component.html',
  styleUrl: './create-album-dialog.component.scss'
})
export class CreateAlbumDialogComponent implements OnInit {
  genresService = inject(GenresService);
  artistsService = inject(ArtistsService);
  toast = inject(ToastrService);
  dialogRef = inject(MatDialogRef<CreateAlbumDialogComponent, OfflineAlbumRequest | null | undefined>);

  selectedArtists: string[] = [];
  selectedGenres: string[] = [];
  artists: Artist[] = [];
  genres: { genre_id: string; name: string }[] = [];
  name = '';
  loading = false;

  @ViewChild(UploadImageBoxComponent) coverBox!: UploadImageBoxComponent;

  onNoClick() {
    this.dialogRef.close(undefined);
  }

  async ngOnInit() {
    try {
      const [genres, artists] = await Promise.all([
        lastValueFrom(this.genresService.list()),
        lastValueFrom(this.artistsService.getAll())
      ]);
      this.genres = genres;
      this.artists = artists;
    } catch {
      this.toast.error('Error', 'Failed to load artists or genres');
    }
  }

  async createOfflineRequest() {
    if (!this.name.trim()) {
      this.toast.error('Error', 'Name is required');
      return;
    }

    if (this.selectedArtists.length === 0) {
      this.toast.error('Error', 'At least one artist must be selected');
      return;
    }

    const coverFile = this.coverBox.image?.file;

    let result: OfflineAlbumRequest = {
      coverFile: coverFile,
      name: this.name,
      selectedArtists: this.selectedArtists,
      selectedGenres: this.selectedGenres
    }

    this.dialogRef.close(result);
  }
}
