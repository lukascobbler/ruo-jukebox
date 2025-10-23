import {Component, inject, Input, OnInit, ViewChild} from '@angular/core';
import {MatDialogRef} from '@angular/material/dialog';
import {MatFormField, MatLabel} from '@angular/material/form-field';
import {MatIconButton} from '@angular/material/button';
import {MatInput} from '@angular/material/input';
import {MatOption} from '@angular/material/core';
import {MatSelect} from '@angular/material/select';
import {UploadSongBoxComponent} from '../upload-song-box/upload-song-box.component';
import {FormsModule} from '@angular/forms';
import {MatProgressSpinner} from '@angular/material/progress-spinner';
import {NgForOf, NgIf} from '@angular/common';
import {UploadImageBoxComponent} from '../upload-image-box/upload-image-box.component';
import {SongsService} from '../../../../services/singles/singles.service';
import {ToastrService} from '../../../../services/toastr/toastr.service';
import {lastValueFrom} from 'rxjs';
import {Artist} from '../../../../models/Artist';
import {GenresService} from '../../../../services/genres/genres.service';
import {ArtistsService} from '../../../../services/artists/artists.service';
import {OfflineSongRequest} from '../../../../services/albums/albums.service';
import {Genre} from '../../../../models/Genre';

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
    NgForOf
  ],
  templateUrl: './create-album-song-dialog.component.html',
  styleUrl: './create-album-song-dialog.component.scss'
})
export class CreateAlbumSongDialogComponent implements OnInit {
  private readonly songsService = inject(SongsService);
  private readonly genresService = inject(GenresService);
  private readonly artistsService = inject(ArtistsService);
  private readonly toast = inject(ToastrService);
  private readonly dialogRef = inject(MatDialogRef<CreateAlbumSongDialogComponent, OfflineSongRequest | null>);
  // @ts-ignore
  @Input() album_id: string;
  @ViewChild(UploadSongBoxComponent) songBox!: UploadSongBoxComponent;
  @ViewChild(UploadImageBoxComponent) coverBox!: UploadImageBoxComponent;

  selectedArtists: Artist[] = [];
  selectedGenres: Genre[] = [];
  artists: Artist[] = [];
  genres: Genre[] = [];
  name = '';
  isEditMode = false;
  loading = false;

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

  async createAlbumSong() {
    if (!this.name.trim()) {
      this.toast.error('Error', 'Name is required');
      return;
    }

    if (this.selectedArtists.length === 0) {
      this.toast.error('Error', 'At least one artist must be selected');
      return;
    }

    const mp3File = this.songBox.file;

    if (!mp3File) {
      this.toast.error('Error', 'Please select a song file');
      return;
    }

    let result: OfflineSongRequest = {
      audioFile: mp3File,
      name: this.name,
      selectedArtists: this.selectedArtists.map(a => a.artist_id),
      selectedGenres: this.selectedGenres.map(g => g.genre_id),
      artists: this.selectedArtists,
      genres: this.selectedGenres,
    }

    this.dialogRef.close(result)
  }
}
