import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatIconButton } from '@angular/material/button';
import { MatInput } from '@angular/material/input';
import { MatOption } from '@angular/material/core';
import { MatSelect } from '@angular/material/select';
import { UploadImageBoxComponent } from '../upload-image-box/upload-image-box.component';
import { MatDialogRef } from '@angular/material/dialog';
import {NgForOf} from '@angular/common';

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
    NgForOf
  ],
  templateUrl: './create-album-dialog.component.html',
  styleUrl: './create-album-dialog.component.scss'
})
export class CreateAlbumDialogComponent {
  name = '';
  selectedArtistId = '';
  selectedGenreIds: string[] = [];
  pictureFile?: File;

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

  constructor(
    public dialogRef: MatDialogRef<CreateAlbumDialogComponent, AlbumDialogData | null | undefined>
  ) {}

  closeDialog() {
    this.dialogRef.close(null);
  }

  onNoClick() {
    this.dialogRef.close(undefined);
  }

  onImageSelected(file: File) {
    this.pictureFile = file;
  }

  confirm() {
    const trimmed = this.name.trim();
    if (!trimmed || !this.selectedArtistId) return;

    this.dialogRef.close({
      name: trimmed,
      artistId: this.selectedArtistId,
      genreIds: this.selectedGenreIds,
      pictureFile: this.pictureFile
    });
  }
}
