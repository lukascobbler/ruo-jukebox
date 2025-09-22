import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-box-missing-icon-medium',
  standalone: true,
  imports: [],
  template: `
    <div class="picture-wrapper">
      <span class="material-symbols-rounded missing-picture-medium">{{ icon_name }}</span>
    </div>
  `,
  styleUrl: './box-missing-icon-medium.component.scss',
})
export class BoxMissingIconMediumComponent {
  @Input() icon_name: string = "";
}
