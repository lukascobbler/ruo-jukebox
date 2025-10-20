import { Component, Input, inject } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatOption } from '@angular/material/core';
import { MatSelect } from '@angular/material/select';
import { MatInput } from '@angular/material/input';
import { MatIconButton } from '@angular/material/button';
import { UploadImageBoxComponent } from '../upload-image-box/upload-image-box.component';
import { NgForOf } from '@angular/common';
import { GenreItem } from '../../../../models/GenreItem';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { ArtistsService } from '../../../../services/artists/artists.service';
import { ToastrService } from '../../../../services/toastr/toastr.service';
import { firstValueFrom } from 'rxjs';

const ALLOWED_CT = new Set([
  'image/jpeg',
  'image/png',
  'image/webp',
  'image/avif',
]);

@Component({
  selector: 'app-create-artist',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatSelect,
    MatOption,
    MatFormField,
    MatInput,
    MatIconButton,
    MatLabel,
    UploadImageBoxComponent,
    NgForOf,
  ],
  templateUrl: './create-artist-dialog.component.html',
  styleUrl: './create-artist-dialog.component.scss',
})
export class CreateArtistDialogComponent {
  @Input() genres: GenreItem[] = [];
  selectedGenreIds: string[] = [];

  private fb = inject(FormBuilder);
  form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(200)]],
    biography: ['', [Validators.required, Validators.maxLength(5000)]],
  });

  selectedFile?: File;
  busy = false;

  constructor(
    public dialogRef: MatDialogRef<CreateArtistDialogComponent, null>,
    private artistsService: ArtistsService,
    public toast: ToastrService
  ) {}

  onFileChosen(file: File | null) {
    if (!file) {
      this.selectedFile = undefined;
      return;
    }
    if (!ALLOWED_CT.has(file.type)) {
      this.toast.error('Invalid image', 'Allowed: JPG, PNG, WEBP, AVIF');
      return;
    }
    this.selectedFile = file;
  }

  trackByGenreId(_i: number, g: GenreItem) {
    return g.id;
  }

  async onCreateClicked() {
    if (this.form.invalid || this.selectedGenreIds.length === 0) {
      this.toast.error(
        'Missing data',
        'Name, Biography and at least one Genre are required.'
      );
      return;
    }
    const name = this.form.value.name!.trim();
    const biography = this.form.value.biography!.trim();
    const genres = this.selectedGenreIds.slice();

    this.busy = true;
    try {
      const created = await firstValueFrom(
        this.artistsService.create({ name, biography, genres })
      );
      if (!created) throw new Error('Create artist failed');

      if (this.selectedFile) {
        const ct = this.selectedFile.type;
        console.log('ct (PUT & presign):', ct);
        const init = await firstValueFrom(
          this.artistsService.initPictureUpload(created.id, ct)
        );
        if (!init?.uploadUrl || !init?.key)
          throw new Error('Init upload failed');

        await firstValueFrom(
          this.artistsService.uploadToS3(init.uploadUrl, this.selectedFile, ct)
        );
        await firstValueFrom(
          this.artistsService.completePictureUpload(created.id, init.key)
        );
      }

      this.toast.success('Artist created', name);
      this.dialogRef.close(null);
    } catch (err: any) {
      const msg =
        err?.error?.message || err?.message || 'Failed to create artist';
      this.toast.error('Create artist error', msg);
    } finally {
      this.busy = false;
    }
  }

  closeDialog() {
    this.dialogRef.close(null);
  }
  onNoClick() {
    this.dialogRef.close(undefined);
  }
  onFileChange(e: Event) {
    const input = e.target as HTMLInputElement | null;
    const file = input?.files?.item(0) ?? null;
    this.onFileChosen(file);
  }
}
