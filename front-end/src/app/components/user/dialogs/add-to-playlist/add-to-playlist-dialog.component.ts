import { Component } from '@angular/core';
import {MatDialogRef} from '@angular/material/dialog';
import {MatFormField} from '@angular/material/form-field';
import {MatOption, MatSelect} from '@angular/material/select';
import {MatIconButton} from '@angular/material/button';

@Component({
  selector: 'app-add-to-playlist',
  standalone: true,
  imports: [
    MatFormField,
    MatSelect,
    MatOption,
    MatIconButton
  ],
  templateUrl: './add-to-playlist-dialog.component.html',
  styleUrl: './add-to-playlist-dialog.component.scss'
})
export class AddToPlaylistDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<AddToPlaylistDialogComponent, null>) {
  }

  closeDialog() {
    this.dialogRef.close(null);
  }

  onNoClick() {
    this.dialogRef.close(undefined);
  }
}
