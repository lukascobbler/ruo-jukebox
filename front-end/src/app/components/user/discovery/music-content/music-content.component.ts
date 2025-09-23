import {Component, inject, OnInit} from '@angular/core';
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
import {Router} from '@angular/router';
import {SearchComponent} from '../../search/search.component';

@Component({
  selector: 'app-music-content',
  standalone: true,
  imports: [
    NgForOf,
    ReactiveFormsModule,
    FormsModule,
    BoxMissingIconXLargeComponent,
    RoundMissingIconXLargeComponent,
    SearchComponent
  ],
  templateUrl: './music-content.component.html',
  styleUrl: './music-content.component.scss'
})
export class MusicContentComponent implements OnInit {
  router = inject(Router);

  searchTerm: string = "";
  albums: Album[] = [
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '2', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '3', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '4', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '5', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '6', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '7', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '8', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
  ];

  artists: Artist[] = [
    {id: '1', name: 'Awesome artist', isSubscribed: false},
    {id: '2', name: 'Awesome artist', isSubscribed: false},
    {id: '3', name: 'Awesome artist', isSubscribed: false},
    {id: '4', name: 'Awesome artist', isSubscribed: false},
    {id: '5', name: 'Awesome artist', isSubscribed: false},
    {id: '6', name: 'Awesome artist', isSubscribed: false},
    {id: '7', name: 'Awesome artist', isSubscribed: false},
    {id: '8', name: 'Awesome artist', isSubscribed: false},
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
