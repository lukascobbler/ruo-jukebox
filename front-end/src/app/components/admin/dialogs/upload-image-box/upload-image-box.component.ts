import {
  ChangeDetectorRef,
  Component,
  EventEmitter,
  inject,
  Input,
  Output,
} from '@angular/core';
import { MatIconButton } from '@angular/material/button';
import { NgIf, NgStyle } from '@angular/common';
import { ToastrService } from '../../../../services/toastr/toastr.service';

@Component({
  selector: 'app-upload-image-box',
  standalone: true,
  imports: [MatIconButton, NgIf, NgStyle],
  templateUrl: './upload-image-box.component.html',
  styleUrl: './upload-image-box.component.scss',
})
export class UploadImageBoxComponent {
  cd = inject(ChangeDetectorRef);

  image: { file: File; url: string } | null = null;
  @Input() accept = '.jpg,.jpeg,.png,.webp,.avif';
  @Output() fileSelected = new EventEmitter<File | null>();

  constructor(private toast: ToastrService) {}

  onSelectNewImage(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    const img = new Image();

    img.onload = () => {
      if (img.naturalWidth === 512 && img.naturalHeight === 512) {
        this.image = { file, url: objectUrl };
        this.fileSelected.emit(file);
        this.cd.detectChanges();
      } else {
        // todo toastr error
        this.toast.error('Image error', 'the image must be 512x512');
        console.log('the image must be 512x512');
        URL.revokeObjectURL(objectUrl);
        input.value = '';
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
  ngOnDestroy(): void {
    if (this.image) URL.revokeObjectURL(this.image.url);
  }
}
