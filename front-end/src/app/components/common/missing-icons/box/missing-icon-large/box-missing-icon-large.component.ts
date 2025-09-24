import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-box-missing-icon-large',
  standalone: true,
  imports: [],
  template: `
    <div class="picture-wrapper">
      <span class="material-symbols-rounded missing-picture-large">{{ icon_name }}</span>
    </div>
  `,
  styleUrl: './box-missing-icon-large.component.scss',
})
export class BoxMissingIconLargeComponent {
  @Input() icon_name: string = "";
}
