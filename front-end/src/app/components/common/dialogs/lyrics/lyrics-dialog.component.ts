import {Component, inject, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {MatFormField, MatLabel} from '@angular/material/form-field';
import {MatInput} from '@angular/material/input';
import {MatIconButton} from '@angular/material/button';
import {MatProgressSpinner} from '@angular/material/progress-spinner';
import {NgIf} from '@angular/common';
import {LyricsService} from '../../../../services/lyrics/lyrics.service';
import {ToastrService} from '../../../../services/toastr/toastr.service';

@Component({
  selector: 'app-lyrics',
  standalone: true,
  imports: [
    MatFormField,
    MatLabel,
    MatInput,
    MatIconButton,
    MatProgressSpinner,
    NgIf
  ],
  templateUrl: './lyrics-dialog.component.html',
  styleUrl: './lyrics-dialog.component.scss'
})
export class LyricsDialogComponent implements OnInit {
  dialogRef = inject(MatDialogRef<LyricsDialogComponent, null>);
  lyricsService = inject(LyricsService);
  toast = inject(ToastrService);
  data = inject(MAT_DIALOG_DATA) as { song_id: string };
  lyrics = "";
  loading = true;

  ngOnInit() {
    this.fetchLyrics();
  }

  onNoClick() {
    this.dialogRef.close(undefined);
  }

  fetchLyrics() {
    this.lyricsService.get(this.data.song_id).subscribe({
      next: value => {
        this.lyrics = value.lyrics;
        this.loading = false;
      },
      error: err => {
        this.toast.error("Error", "Error fetching lyrics: " + err);
        this.lyrics = "Lyrics not found";
        this.loading = false;
      }
    })
  }
}
