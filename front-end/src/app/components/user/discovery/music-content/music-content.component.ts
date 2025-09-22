import {Component, OnInit} from '@angular/core';
import {MatFormField, MatSuffix} from "@angular/material/form-field";
import {MatInput} from "@angular/material/input";
import {NgForOf} from "@angular/common";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {
  BoxMissingIconXLargeComponent
} from '../../../common/missing-icons/box/missing-icon-x-large/box-missing-icon-x-large.component';
import {
  RoundMissingIconXLargeComponent
} from '../../../common/missing-icons/round/round-missing-icon-x-large/round-missing-icon-x-large.component';
import {Album} from '../../../../models/Album';
import {Artist} from '../../../../models/Artist';

@Component({
  selector: 'app-music-content',
  standalone: true,
  imports: [
    MatFormField,
    MatInput,
    MatSuffix,
    NgForOf,
    ReactiveFormsModule,
    FormsModule,
    BoxMissingIconXLargeComponent,
    RoundMissingIconXLargeComponent
  ],
  templateUrl: './music-content.component.html',
  styleUrl: './music-content.component.scss'
})
export class MusicContentComponent implements OnInit {
  searchTerm: string = "";
  albums: Album[] = [
    {id: '', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
  ];

  artists: Artist[] = [
    {id: '', name: 'Awesome artist', isSubscribed: false},
    {id: '', name: 'Awesome artist', isSubscribed: false},
    {id: '', name: 'Awesome artist', isSubscribed: false},
    {id: '', name: 'Awesome artist', isSubscribed: false},
    {id: '', name: 'Awesome artist', isSubscribed: false},
    {id: '', name: 'Awesome artist', isSubscribed: false},
    {id: '', name: 'Awesome artist', isSubscribed: false},
    {id: '', name: 'Awesome artist', isSubscribed: false},
  ];

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
