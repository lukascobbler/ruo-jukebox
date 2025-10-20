import {Component, inject, ViewChild} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatIconButton } from '@angular/material/button';
import { MatInput } from '@angular/material/input';
import { MatOption } from '@angular/material/core';
import { MatSelect } from '@angular/material/select';
import { UploadImageBoxComponent } from '../upload-image-box/upload-image-box.component';
import { MatDialogRef } from '@angular/material/dialog';
import {NgForOf, NgIf} from '@angular/common';
import {lastValueFrom} from 'rxjs';
import {AlbumsService} from '../../../../services/albums/albums.service';
import {ToastrService} from '../../../../services/toastr/toastr.service';
import {MatProgressSpinner} from '@angular/material/progress-spinner';

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
export class CreateAlbumDialogComponent {
  albumsService = inject(AlbumsService);
  toast = inject(ToastrService);
  dialogRef = inject(MatDialogRef<CreateAlbumDialogComponent, string | null | undefined>);
  selectedArtistId = '';
  selectedGenreIds: string[] = [];

  selectedArtists: string[] = [];
  selectedGenres: string[] = [];
  name = '';
  isEditMode = false;
  loading = false;

  @ViewChild(UploadImageBoxComponent) coverBox!: UploadImageBoxComponent;

  // placeholder lists (will later come from real services)
  availableArtists = [
    { id: 'artist1', name: 'Awesome artist 1' },
    { id: 'artist2', name: 'Awesome artist 2' },
    { id: 'artist3', name: 'Awesome artist 3' }
  ];

  availableGenres = [
    { id: 'rock', name: 'Rock' },
    { id: 'pop', name: 'Pop' },
    { id: 'jazz', name: 'Jazz' },
    { id: 'classical', name: 'Classical' }
  ];

  onNoClick() {
    this.dialogRef.close(undefined);
  }

  async create() {
    if (this.isEditMode) {
      // await this.updateAlbum(); todo
      return;
    }

    const coverFile = this.coverBox.image?.file;

    this.loading = true;
    try {
      const initRes = await lastValueFrom(this.albumsService.initUpload({
        name: this.name,
        artists: this.selectedArtists,
        genres: this.selectedGenres,
        cover_filename: coverFile?.name
      }));
      await fetch(initRes.upload_url, {method: 'PUT'});
      if (coverFile && initRes.cover_upload_url)
        await fetch(initRes.cover_upload_url, {method: 'PUT', body: coverFile});
      await lastValueFrom(this.albumsService.completeUpload(initRes.album_id));

      this.toast.success('Success', 'Song successfully created');
      this.dialogRef.close(initRes.album_id);
    } catch {
      this.toast.error('Error', 'Unable to upload the album');
    } finally {
      this.loading = false;
    }
  }
}
