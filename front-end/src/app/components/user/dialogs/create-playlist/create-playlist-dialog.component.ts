import { Component } from '@angular/core';
import {MatFormField, MatLabel} from "@angular/material/form-field";
import {MatIconButton} from "@angular/material/button";
import {MatOption} from "@angular/material/core";
import {MatSelect} from "@angular/material/select";
import {MatDialogRef} from '@angular/material/dialog';
import {MatInput} from '@angular/material/input';

@Component({
  selector: 'app-create-playlist',
  standalone: true,
  imports: [
    MatFormField,
    MatIconButton,
    MatLabel,
    MatInput
  ],
  templateUrl: './create-playlist-dialog.component.html',
  styleUrl: './create-playlist-dialog.component.scss'
})
export class CreatePlaylistDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<CreatePlaylistDialogComponent, null>) {
  }

  closeDialog() {
    this.dialogRef.close(null);
  }

  onNoClick() {
    this.dialogRef.close(undefined);
  }
}
