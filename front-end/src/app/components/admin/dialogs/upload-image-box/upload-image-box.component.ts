import {ChangeDetectorRef, Component, inject} from '@angular/core';
import {NgIf} from '@angular/common';
import {MatIconButton} from '@angular/material/button';

@Component({
  selector: 'app-upload-image-box',
  standalone: true,
  imports: [NgIf, MatIconButton],
  templateUrl: './upload-image-box.component.html',
  styleUrls: ['./upload-image-box.component.scss']
})
export class UploadImageBoxComponent {
  private cd = inject(ChangeDetectorRef);
  image: { file: File; url: string } | null = null;

  onSelectNewImage(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    const img = new Image();

    img.onload = () => {
      this.image = {file, url: objectUrl};
      this.cd.detectChanges();
    };

    img.src = objectUrl;
  }

  onRemoveImage(event: Event, fileInput: HTMLInputElement) {
    event.stopPropagation();
    if (this.image) URL.revokeObjectURL(this.image.url);
    this.image = null;
    fileInput.value = '';
  }

  onBoxClick(fileInput: HTMLInputElement) {
    if (!this.image) fileInput.click();
  }
}
