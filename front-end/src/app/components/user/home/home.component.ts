import {Component, OnInit} from '@angular/core';
import {NgForOf} from '@angular/common';
import {SongTableComponent} from '../song-table/song-table.component';
import {MatFormField, MatSuffix} from '@angular/material/form-field';
import {MatInput} from '@angular/material/input';
import {FormsModule} from '@angular/forms';
import {
  BoxMissingIconXLargeComponent
} from '../../common/missing-icons/box/missing-icon-x-large/box-missing-icon-x-large.component';
import {
  RoundMissingIconXLargeComponent
} from '../../common/missing-icons/round/round-missing-icon-x-large/round-missing-icon-x-large.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    SongTableComponent,
    MatFormField,
    MatInput,
    FormsModule,
    MatSuffix,
    NgForOf,
    RoundMissingIconXLargeComponent,
    RoundMissingIconXLargeComponent,
    BoxMissingIconXLargeComponent,
    RoundMissingIconXLargeComponent
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  searchTerm: string = "";

  ngOnInit() {
    const containers = document.querySelectorAll('.horizontal-scroller');

    containers.forEach(container => {
      container.addEventListener(
        'wheel',
        e => {
          e.preventDefault();
          (container as HTMLElement).scrollLeft += (e as WheelEvent).deltaY;
        },
        { passive: false }
      );
    });
  }
}
