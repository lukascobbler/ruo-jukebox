import {ChangeDetectorRef, Component, inject} from '@angular/core';
import {NgIf, NgStyle} from '@angular/common';
import {MatIconButton} from '@angular/material/button';

@Component({
  selector: 'app-upload-song-box',
  standalone: true,
  imports: [
    NgIf,
    NgStyle,
    MatIconButton
  ],
  templateUrl: './upload-song-box.component.html',
  styleUrl: './upload-song-box.component.scss'
})
export class UploadSongBoxComponent {
  cd = inject(ChangeDetectorRef);

  file: File | null = null;

  allowedAudioTypes = [
    'audio/mpeg',
    'audio/flac',
    'audio/wav',
    'audio/ogg',
    'audio/mp4',
    'audio/aac'
  ];

  onSelectNewFile(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    if (!this.isAudioFile(file)) {
      // todo toastr error
      console.info(`not a supported audio file`);
      input.value = ''; // reset input so user can select again
      return;
    }

    this.file = file;
    this.cd.detectChanges();
  }

  onRemoveFile(event: Event, fileInput: HTMLInputElement) {
    event.stopPropagation();
    this.file = null;
    fileInput.value = '';
  }

  handleBoxClick(fileInput: HTMLInputElement) {
    if (!this.file) {
      fileInput.click();
    }
  }

  private isAudioFile(file: File): boolean {
    if (this.allowedAudioTypes.includes(file.type)) return true;

    const extension = file.name.split('.').pop()?.toLowerCase();
    return ['mp3', 'flac', 'wav', 'ogg', 'm4a', 'aac'].includes(extension || '');
  }
}
