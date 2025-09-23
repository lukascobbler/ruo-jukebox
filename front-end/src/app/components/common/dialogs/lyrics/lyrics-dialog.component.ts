import {Component, inject} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {MatFormField, MatLabel} from '@angular/material/form-field';
import {MatInput} from '@angular/material/input';
import {MatIconButton} from '@angular/material/button';

@Component({
  selector: 'app-lyrics',
  standalone: true,
  imports: [
    MatFormField,
    MatLabel,
    MatInput,
    MatIconButton
  ],
  templateUrl: './lyrics-dialog.component.html',
  styleUrl: './lyrics-dialog.component.scss'
})
export class LyricsDialogComponent {
  dialogRef = inject(MatDialogRef<LyricsDialogComponent, null>);
  data = inject(MAT_DIALOG_DATA) as { lyrics: string };
  lyrics = this.data.lyrics;

  onNoClick() {
    this.dialogRef.close(undefined);
  }
}
