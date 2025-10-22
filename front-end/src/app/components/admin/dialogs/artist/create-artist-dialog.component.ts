import { Component, Input, ViewChild, inject } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatOption } from '@angular/material/core';
import { MatSelect } from '@angular/material/select';
import { MatInput } from '@angular/material/input';
import { MatIconButton } from '@angular/material/button';
import { UploadImageBoxComponent } from '../upload-image-box/upload-image-box.component';
import { NgForOf, NgIf } from '@angular/common';
import { GenreItem } from '../../../../models/GenreItem';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { ArtistsService } from '../../../../services/artists/artists.service';
import { ToastrService } from '../../../../services/toastr/toastr.service';
import { firstValueFrom } from 'rxjs';
import { MatProgressSpinner } from '@angular/material/progress-spinner';

const ALLOWED_CT = new Set(['image/jpeg', 'image/png', 'image/webp', 'image/avif']);

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
    biography: ['', [Validators.maxLength(5000)]],
  });

  busy = false;

  constructor(
    public dialogRef: MatDialogRef<CreateArtistDialogComponent, null>,
    private artistsService: ArtistsService,
    public toast: ToastrService
  ) {}

  trackByGenreId(_i: number, g: GenreItem) {
    return g.genre_id;
  }

  async onCreateClicked() {
    if (this.form.invalid) {
      this.toast.error('Missing data', 'Name is required.');
      return;
    }

    const name = this.form.value.name!.trim();
    const biography = this.form.value.biography?.trim();
    const genres = this.selectedGenreIds.slice();
    const file = this.imageBox?.image?.file ?? null;

    this.busy = true;
    try {
      const init = await firstValueFrom(
        this.artistsService.create({ name, biography, genres, cover: !!file })
      );
      if (!init.artist_id) throw new Error('Init upload failed');

      if (file && init.cover_url)
        await fetch(init.cover_url, {method: 'PUT', body: file});

      const completed = await firstValueFrom(
        this.artistsService.completeUpload({
          artist_id: init.artist_id,
          name,
          biography,
          genres,
        })
      );

      this.toast.success('Artist created', completed.name);
      this.dialogRef.close(null);
    } catch (err: any) {
      const msg = err?.error?.message || err?.message || 'Failed to create artist';
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
