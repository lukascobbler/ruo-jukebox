import { Component } from '@angular/core';
import {MatFormField, MatLabel} from '@angular/material/form-field';
import {MatIconButton} from '@angular/material/button';
import {MatInput} from '@angular/material/input';
import {MatOption} from '@angular/material/core';
import {MatSelect} from '@angular/material/select';
import {UploadImageBoxComponent} from '../upload-image-box/upload-image-box.component';
import {MatDialogRef} from '@angular/material/dialog';

@Component({
  selector: 'app-album',
  standalone: true,
  imports: [
    MatFormField,
    MatIconButton,
    MatInput,
    MatLabel,
    MatOption,
    MatSelect,
    UploadImageBoxComponent
  ],
  templateUrl: './create-album-dialog.component.html',
  styleUrl: './create-album-dialog.component.scss'
})
export class CreateAlbumDialogComponent {
  constructor(public dialogRef: MatDialogRef<CreateAlbumDialogComponent, null>) {}

  closeDialog() {
    this.dialogRef.close(null);
  }

  onNoClick() {
    this.dialogRef.close(undefined);
  }
}
