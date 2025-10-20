import { Component, Input, ViewChild, inject } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatOption } from '@angular/material/core';
import { MatSelect } from '@angular/material/select';
import { MatInput } from '@angular/material/input';
import { MatIconButton } from '@angular/material/button';
import { UploadImageBoxComponent } from '../upload-image-box/upload-image-box.component';
import {NgForOf, NgIf} from '@angular/common';
import { GenreItem } from '../../../../models/GenreItem';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { ArtistsService } from '../../../../services/artists/artists.service';
import { ToastrService } from '../../../../services/toastr/toastr.service';
import { firstValueFrom } from 'rxjs';
import {MatProgressSpinner} from '@angular/material/progress-spinner';

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
    MatProgressSpinner,
    NgIf,
  ],
  templateUrl: './create-artist-dialog.component.html',
  styleUrl: './create-artist-dialog.component.scss',
})
export class CreateArtistDialogComponent {
  @Input() genres: GenreItem[] = [];
  selectedGenreIds: string[] = [];
  @ViewChild('imgBox') imageBox?: UploadImageBoxComponent;

  private fb = inject(FormBuilder);
  form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(200)]],
    biography: ['', [Validators.required, Validators.maxLength(5000)]],
  });

  busy = false;

  constructor(
    public dialogRef: MatDialogRef<CreateArtistDialogComponent, null>,
    private artistsService: ArtistsService,
    public toast: ToastrService
  ) {}

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
    const file = this.imageBox?.image?.file ?? null;


    this.busy = true;
    try {
      const created = await firstValueFrom(
        this.artistsService.create({ name, biography, genres })
      );
      if (!created) throw new Error('Create artist failed');

      if (file) {
        const ct = file.type;
        console.log('ct (PUT & presign):', ct);
        const init = await firstValueFrom(
          this.artistsService.initPictureUpload(created.id, ct)
        );
        if (!init?.uploadUrl || !init?.key)
          throw new Error('Init upload failed');

        await firstValueFrom(
          this.artistsService.uploadToS3(init.uploadUrl, file, ct)
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
}
