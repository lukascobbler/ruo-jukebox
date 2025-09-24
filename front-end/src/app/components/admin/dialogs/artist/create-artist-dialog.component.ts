import { Component } from '@angular/core';
import {MatDialogRef} from '@angular/material/dialog';
import {MatFormField, MatLabel, MatOption, MatSelect} from '@angular/material/select';
import {MatInput} from '@angular/material/input';
import {MatIconButton} from '@angular/material/button';
import {UploadImageBoxComponent} from '../upload-image-box/upload-image-box.component';

@Component({
  selector: 'app-create-artist',
  standalone: true,
  imports: [
    MatSelect,
    MatOption,
    MatFormField,
    MatInput,
    MatIconButton,
    MatLabel,
    UploadImageBoxComponent
  ],
  templateUrl: './create-artist-dialog.component.html',
  styleUrl: './create-artist-dialog.component.scss'
})
export class CreateArtistDialogComponent {
  constructor(public dialogRef: MatDialogRef<CreateArtistDialogComponent, null>) {}

  closeDialog() {
    this.dialogRef.close(null);
  }

  onNoClick() {
    this.dialogRef.close(undefined);
  }
}
