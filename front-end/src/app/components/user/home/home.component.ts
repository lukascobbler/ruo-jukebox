import {Component, inject, OnInit} from '@angular/core';
import {NgForOf} from '@angular/common';
import {SongTableComponent} from '../song-table/song-table.component';
import {FormsModule} from '@angular/forms';
import {
  BoxMissingIconXLargeComponent
} from '../../common/missing-icons/box/missing-icon-x-large/box-missing-icon-x-large.component';
import {
  RoundMissingIconXLargeComponent
} from '../../common/missing-icons/round/round-missing-icon-x-large/round-missing-icon-x-large.component';
import {Album} from '../../../models/album/Album';
import {Artist} from '../../../models/Artist';
import {Router} from '@angular/router';
import {SearchComponent} from '../search/search.component';
import {AuthService} from '../../../services/auth/auth.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    SongTableComponent,
    FormsModule,
    NgForOf,
    RoundMissingIconXLargeComponent,
    RoundMissingIconXLargeComponent,
    BoxMissingIconXLargeComponent,
    RoundMissingIconXLargeComponent,
    SearchComponent
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  router = inject(Router);
  auth = inject(AuthService);

  albums: Album[] = [
    { id: '1', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], released: false },
    { id: '2', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '2', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], released: false },
    { id: '3', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '3', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], released: false },
    { id: '4', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '4', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], released: false },
    { id: '5', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '5', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], released: false },
    { id: '6', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '6', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], released: false },
    { id: '7', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '7', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], released: false },
    { id: '8', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '8', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], released: false },
  ];

  artists: Artist[] = [
    // { id: '', name: 'Awesome artist', biography: '', genres: [], isSubscribed: false },
    // { id: '', name: 'Awesome artist', biography: '', genres: [], isSubscribed: false },
    // { id: '', name: 'Awesome artist', biography: '', genres: [], isSubscribed: false },
    // { id: '', name: 'Awesome artist', biography: '', genres: [], isSubscribed: false },
    // { id: '', name: 'Awesome artist', biography: '', genres: [], isSubscribed: false },
    // { id: '', name: 'Awesome artist', biography: '', genres: [], isSubscribed: false },
    // { id: '', name: 'Awesome artist', biography: '', genres: [], isSubscribed: false },
    // { id: '', name: 'Awesome artist', biography: '', genres: [], isSubscribed: false },
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
