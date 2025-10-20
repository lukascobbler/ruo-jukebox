import {ChangeDetectorRef, Component, inject, Input, OnChanges, SimpleChanges} from '@angular/core';
import {NgIf} from '@angular/common';
import {MatIconButton} from '@angular/material/button';

@Component({
  selector: 'app-upload-image-box',
  standalone: true,
  imports: [NgIf, MatIconButton],
  templateUrl: './upload-image-box.component.html',
  styleUrls: ['./upload-image-box.component.scss']
})
export class UploadImageBoxComponent implements OnChanges {
  private cd = inject(ChangeDetectorRef);
  @Input() imageUrl?: string; // prefilled cover URL
  image: { file: File | null; url: string } | null = null;

  ngOnChanges(changes: SimpleChanges) {
    if (changes['imageUrl'] && this.imageUrl) {
      this.image = { file: null, url: this.imageUrl };
      this.cd.detectChanges();
    }
  }

  onSelectNewImage(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    this.image = { file, url: objectUrl };
    this.cd.detectChanges();
  }

  onRemoveImage(event: Event, fileInput: HTMLInputElement) {
    event.stopPropagation();
    if (this.image && this.image.file) URL.revokeObjectURL(this.image.url);
    this.image = null;
    fileInput.value = '';
    this.cd.detectChanges();
  }

  onBoxClick(fileInput: HTMLInputElement) {
    if (!this.image) fileInput.click();
  }
}
