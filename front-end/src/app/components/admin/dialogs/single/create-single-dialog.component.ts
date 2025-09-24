import { Component } from '@angular/core';
import {MatFormField, MatLabel} from '@angular/material/form-field';
import {MatIconButton} from '@angular/material/button';
import {MatInput} from '@angular/material/input';
import {MatOption} from '@angular/material/core';
import {MatSelect} from '@angular/material/select';
import {UploadImageBoxComponent} from '../upload-image-box/upload-image-box.component';
import {MatDialogRef} from '@angular/material/dialog';
import {UploadSongBoxComponent} from '../upload-song-box/upload-song-box.component';

@Component({
  selector: 'app-single',
  standalone: true,
  imports: [
    MatFormField,
    MatIconButton,
    MatInput,
    MatLabel,
    MatOption,
    MatSelect,
    UploadImageBoxComponent,
    UploadSongBoxComponent
  ],
  templateUrl: './create-single-dialog.component.html',
  styleUrl: './create-single-dialog.component.scss'
})
export class CreateSingleDialogComponent {
  constructor(public dialogRef: MatDialogRef<CreateSingleDialogComponent, null>) {}

  closeDialog() {
    this.dialogRef.close(null);
  }

  onNoClick() {
    this.dialogRef.close(undefined);
  }
}
