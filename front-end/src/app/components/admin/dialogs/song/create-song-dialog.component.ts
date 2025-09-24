import { Component } from '@angular/core';
import {MatDialogRef} from '@angular/material/dialog';
import {MatFormField, MatLabel} from '@angular/material/form-field';
import {MatIconButton} from '@angular/material/button';
import {MatInput} from '@angular/material/input';
import {MatOption} from '@angular/material/core';
import {MatSelect} from '@angular/material/select';
import {UploadImageBoxComponent} from '../upload-image-box/upload-image-box.component';
import {UploadSongBoxComponent} from '../upload-song-box/upload-song-box.component';

@Component({
  selector: 'app-song',
  standalone: true,
  imports: [
    MatFormField,
    MatIconButton,
    MatInput,
    MatLabel,
    MatOption,
    MatSelect,
    UploadSongBoxComponent
  ],
  templateUrl: './create-song-dialog.component.html',
  styleUrl: './create-song-dialog.component.scss'
})
export class CreateSongDialogComponent {
  constructor(public dialogRef: MatDialogRef<CreateSongDialogComponent, null>) {}

  closeDialog() {
    this.dialogRef.close(null);
  }

  onNoClick() {
    this.dialogRef.close(undefined);
  }
}
