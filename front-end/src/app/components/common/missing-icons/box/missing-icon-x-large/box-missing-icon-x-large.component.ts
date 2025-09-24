import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-box-missing-icon-x-large',
  standalone: true,
  imports: [],
  template: `
    <div class="picture-wrapper">
      <span class="material-symbols-rounded missing-picture-x-large">{{ icon_name }}</span>
    </div>
  `,
  styleUrl: './box-missing-icon-x-large.component.scss',
})
export class BoxMissingIconXLargeComponent {
  @Input() icon_name: string = "";
}
