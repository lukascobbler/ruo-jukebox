import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-round-missing-icon-large',
  standalone: true,
  imports: [],
  template: `
    <div class="picture-wrapper">
      <span class="material-symbols-rounded missing-picture-large">{{ icon_name }}</span>
    </div>
  `,
  styleUrl: './round-missing-icon-large.component.scss',
})
export class RoundMissingIconLargeComponent {
  @Input() icon_name: string = "";
}
