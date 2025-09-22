import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-round-missing-icon-x-large',
  standalone: true,
  imports: [],
  template: `
    <div class="picture-wrapper">
      <span class="material-symbols-rounded missing-picture-x-large">{{ icon_name }}</span>
    </div>
  `,
  styleUrl: './round-missing-icon-x-large.component.scss',
})
export class RoundMissingIconXLargeComponent {
  @Input() icon_name: string = "";
}
