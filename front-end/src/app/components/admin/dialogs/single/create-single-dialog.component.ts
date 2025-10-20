import {UploadImageBoxComponent} from '../upload-image-box/upload-image-box.component';
import {UploadSongBoxComponent} from '../upload-song-box/upload-song-box.component';
import {SongsService} from '../../../../services/songs/songs.service';
import {MatFormField, MatLabel} from '@angular/material/form-field';
import {Component, inject, ViewChild} from '@angular/core';
import {MatIconButton} from '@angular/material/button';
import {MatDialogRef} from '@angular/material/dialog';
import {MatSelect} from '@angular/material/select';
import {MatInput} from '@angular/material/input';
import {MatOption} from '@angular/material/core';
import {FormsModule} from '@angular/forms';
import {lastValueFrom} from 'rxjs';
import {ToastrService} from '../../../../services/toastr/toastr.service';

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
    FormsModule
  ],
  styleUrls: ['./create-single-dialog.component.scss']
})
export class CreateSingleDialogComponent {
  dialogRef = inject(MatDialogRef<CreateSingleDialogComponent, string | null>);
  songsService = inject(SongsService);
  toast = inject(ToastrService);

  @ViewChild(UploadSongBoxComponent) songBox!: UploadSongBoxComponent;
  @ViewChild(UploadImageBoxComponent) coverBox!: UploadImageBoxComponent;

  selectedArtists: string[] = [];
  selectedGenres: string[] = [];
  name = '';

  onNoClick() {
    this.dialogRef.close(undefined);
  }

  async createSong() {
    const mp3File = this.songBox.file;
    const coverFile = this.coverBox.image?.file;

    if (!mp3File) {
      this.toast.error('Error', 'Please select a song file');
      return;
    }

    try {
      const initRes = await lastValueFrom(this.songsService.initUpload({
        name: this.name,
        artists: this.selectedArtists,
        genres: this.selectedGenres,
        filename: mp3File.name,
        cover_filename: coverFile?.name
      }));
      await fetch(initRes.upload_url, {method: 'PUT', body: mp3File});
      if (coverFile && initRes.cover_upload_url)
        await fetch(initRes.cover_upload_url, {method: 'PUT', body: coverFile});
      await lastValueFrom(this.songsService.completeUpload(initRes.song_id));
      this.dialogRef.close(initRes.song_id);
    } catch (err) {
      this.toast.error('Error', 'Unable to upload the song');
    }
  }
}
