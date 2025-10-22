import {UploadImageBoxComponent} from '../upload-image-box/upload-image-box.component';
import {UploadSongBoxComponent} from '../upload-song-box/upload-song-box.component';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {Component, inject, ViewChild, Inject, OnInit} from '@angular/core';
import {ToastrService} from '../../../../services/toastr/toastr.service';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {SongsService} from '../../../../services/singles/singles.service';
import {MatFormField, MatLabel} from '@angular/material/form-field';
import {MatIconButton} from '@angular/material/button';
import {MatSelect} from '@angular/material/select';
import {MatInput} from '@angular/material/input';
import {MatOption} from '@angular/material/core';
import {FormsModule} from '@angular/forms';
import {NgIf, NgFor} from '@angular/common';
import {lastValueFrom} from 'rxjs';
import {GenresService} from '../../../../services/genres/genres.service';

@Component({
  selector: 'app-single',
  templateUrl: './create-single-dialog.component.html',
  standalone: true,
  imports: [
    MatFormField,
    MatOption,
    MatSelect,
    MatLabel,
    MatInput,
    MatIconButton,
    UploadSongBoxComponent,
    UploadImageBoxComponent,
    FormsModule,
    MatProgressSpinnerModule,
    NgIf,
    NgFor
  ],
  styleUrls: ['./create-single-dialog.component.scss']
})
export class CreateSingleDialogComponent implements OnInit {
  private readonly songsService = inject(SongsService);
  private readonly genresService = inject(GenresService);
  private readonly toast = inject(ToastrService);
  private readonly dialogRef = inject(MatDialogRef<CreateSingleDialogComponent, string | null>);
  @ViewChild(UploadSongBoxComponent) songBox!: UploadSongBoxComponent;
  @ViewChild(UploadImageBoxComponent) coverBox!: UploadImageBoxComponent;

  constructor(@Inject(MAT_DIALOG_DATA) public data: any) {
  }

  selectedArtists: string[] = [];
  selectedGenres: string[] = [];
  genres: { genre_id: string; name: string }[] = [];
  name = '';
  isEditMode = false;
  loading = false;

  async ngOnInit() {
    if (this.data) {
      this.isEditMode = true;
      this.name = this.data.name || '';
      this.selectedArtists = this.data.artists || [];
      this.selectedGenres = this.data.genres || [];
    }

    try {
      this.genres = await lastValueFrom(this.genresService.list());
    } catch {
      this.toast.error('Error', 'Failed to load genres');
    }
  }

  onNoClick() {
    this.dialogRef.close(undefined);
  }

  async createSong() {
    if (this.isEditMode) {
      await this.updateSong();
      return;
    }

    const mp3File = this.songBox.file;
    const coverFile = this.coverBox.image?.file;

    if (!mp3File) {
      this.toast.error('Error', 'Please select a song file');
      return;
    }

    this.loading = true;
    try {
      const initRes = await lastValueFrom(this.songsService.initUpload({cover: Boolean(coverFile)}));

      await fetch(initRes.audio_url, {method: 'PUT', body: mp3File});

      if (coverFile && initRes.cover_url)
        await fetch(initRes.cover_url, {method: 'PUT', body: coverFile});

      await lastValueFrom(this.songsService.completeUpload({
        name: this.name,
        song_id: initRes.song_id,
        single_id: initRes.single_id,
        artists: this.selectedArtists,
        genres: this.selectedGenres,
      }));

      this.toast.success('Success', 'Song successfully created');
      this.dialogRef.close(initRes.song_id);
    } catch {
      this.toast.error('Error', 'Unable to upload the song');
    } finally {
      this.loading = false;
    }
  }

  private async updateSong() {
    this.loading = true;
    try {
      const newCoverFile = this.coverBox.image?.file;
      const newAudioFile = this.songBox.file;
      const hasNewCover = !!newCoverFile;
      const hasNewAudio = !!newAudioFile;

      const body: any = {
        name: this.name,
        artist_ids: this.selectedArtists,
        genre_ids: this.selectedGenres,
      };

      if (hasNewCover) body.cover_filename = newCoverFile.name;
      if (hasNewAudio) body.audio_filename = newAudioFile.name;

      const updateRes = await lastValueFrom(this.songsService.updateSingle(this.data.song_id, body));

      if (hasNewCover && updateRes.cover_upload_url)
        await fetch(updateRes.cover_upload_url, {method: 'PUT', body: newCoverFile});

      if (hasNewAudio && updateRes.audio_upload_url)
        await fetch(updateRes.audio_upload_url, {method: 'PUT', body: newAudioFile});

      this.toast.success('Success', 'Song updated successfully');
      this.dialogRef.close(this.data.song_id);
    } catch {
      this.toast.error('Error', 'Failed to update song');
    } finally {
      this.loading = false;
    }
  }
}
