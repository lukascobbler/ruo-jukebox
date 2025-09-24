import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-box-missing-icon-small',
  standalone: true,
  imports: [],
  template: `
    <div class="picture-wrapper">
      <span class="material-symbols-rounded missing-picture-small">{{ icon_name }}</span>
    </div>
  `,
  styleUrl: './box-missing-icon-small.component.scss',
})
export class BoxMissingIconSmallComponent {
  @Input() icon_name: string = "";
}
