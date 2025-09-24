import {ChangeDetectorRef, Component, inject} from '@angular/core';
import {MatIconButton} from '@angular/material/button';
import {NgIf, NgStyle} from '@angular/common';

@Component({
  selector: 'app-upload-box',
  standalone: true,
  imports: [
    MatIconButton,
    NgIf,
    NgStyle,
  ],
  templateUrl: './upload-box.component.html',
  styleUrl: './upload-box.component.scss'
})
export class UploadBoxComponent {
  cd = inject(ChangeDetectorRef);

  image: { file: File; url: string } | null = null;

  onSelectNewImage(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    const img = new Image();

    img.onload = () => {
      if (img.naturalWidth === 512 && img.naturalHeight === 512) {
        this.image = { file, url: objectUrl };
        this.cd.detectChanges();
      } else {
        // todo toastr error
        console.log('the image must be 512x512')
        URL.revokeObjectURL(objectUrl);
      }
    };

    img.src = objectUrl;
  }

  onRemoveImage(event: Event, fileInput: HTMLInputElement) {
    event.stopPropagation();
    if (this.image) {
      URL.revokeObjectURL(this.image.url);
    }
    this.image = null;
    fileInput.value = '';
  }

  handleBoxClick(fileInput: HTMLInputElement) {
    if (!this.image) {
      fileInput.click();
    }
  }
}
