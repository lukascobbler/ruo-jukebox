import {Component, Inject, inject, Input, ViewChild} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {MatFormField, MatLabel} from '@angular/material/form-field';
import {MatIconButton} from '@angular/material/button';
import {MatInput} from '@angular/material/input';
import {MatOption} from '@angular/material/core';
import {MatSelect} from '@angular/material/select';
import {UploadSongBoxComponent} from '../upload-song-box/upload-song-box.component';
import {FormsModule} from '@angular/forms';
import {MatProgressSpinner} from '@angular/material/progress-spinner';
import {NgIf} from '@angular/common';
import {UploadImageBoxComponent} from '../upload-image-box/upload-image-box.component';
import {SongsService} from '../../../../services/songs/songs.service';
import {ToastrService} from '../../../../services/toastr/toastr.service';
import {lastValueFrom} from 'rxjs';

@Component({
  selector: 'app-album-song',
  standalone: true,
  imports: [
    MatFormField,
    MatIconButton,
    MatInput,
    MatLabel,
    MatOption,
    MatSelect,
    UploadSongBoxComponent,
    FormsModule,
    MatProgressSpinner,
    NgIf,
    UploadImageBoxComponent
  ],
  templateUrl: './create-album-song-dialog.component.html',
  styleUrl: './create-album-song-dialog.component.scss'
})
export class CreateAlbumSongDialogComponent {
  private readonly songsService = inject(SongsService);
  private readonly toast = inject(ToastrService);
  private readonly dialogRef = inject(MatDialogRef<CreateAlbumSongDialogComponent, string | null>);
  // @ts-ignore
  @Input() album_id: string;
  @ViewChild(UploadSongBoxComponent) songBox!: UploadSongBoxComponent;
  @ViewChild(UploadImageBoxComponent) coverBox!: UploadImageBoxComponent;

  constructor(@Inject(MAT_DIALOG_DATA) public data: any) {}

  selectedArtists: string[] = [];
  selectedGenres: string[] = [];
  name = '';
  isEditMode = false;
  loading = false;

  ngOnInit() {
    if (this.data) {
      this.isEditMode = true;
      this.name = this.data.name || '';
      this.selectedArtists = this.data.artists || [];
      this.selectedGenres = this.data.genres || [];
    }
  }

  onNoClick() {
    this.dialogRef.close(undefined);
  }

  async createSong() {
    if (this.isEditMode) {
      // await this.updateSong(); todo
      return;
    }

    const mp3File = this.songBox.file;

    if (!mp3File) {
      this.toast.error('Error', 'Please select a song file');
      return;
    }

    this.loading = true;
    try {
      const initRes = await lastValueFrom(this.songsService.initUpload({
        name: this.name,
        artists: this.selectedArtists,
        genres: this.selectedGenres,
        filename: mp3File.name,
        album_id: this.album_id
      }));
      await fetch(initRes.upload_url, {method: 'PUT', body: mp3File});
      await lastValueFrom(this.songsService.completeUpload(initRes.song_id));

      this.toast.success('Success', 'Song successfully created');
      this.dialogRef.close(initRes.song_id);
    } catch {
      this.toast.error('Error', 'Unable to upload the song');
    } finally {
      this.loading = false;
    }
  }
}
