import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-round-missing-icon-small',
  standalone: true,
  imports: [],
  template: `
    <div class="picture-wrapper">
      <span class="material-symbols-rounded missing-picture-small">{{ icon_name }}</span>
    </div>
  `,
  styleUrl: './round-missing-icon-small.component.scss',
})
export class RoundMissingIconSmallComponent {
  @Input() icon_name: string = "";
}
