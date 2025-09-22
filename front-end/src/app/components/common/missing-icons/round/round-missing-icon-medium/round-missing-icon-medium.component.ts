import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-round-missing-icon-medium',
  standalone: true,
  imports: [],
  template: `
    <div class="picture-wrapper">
      <span class="material-symbols-rounded missing-picture-medium">{{ icon_name }}</span>
    </div>
  `,
  styleUrl: './round-missing-icon-medium.component.scss',
})
export class RoundMissingIconMediumComponent {
  @Input() icon_name: string = "";
}
