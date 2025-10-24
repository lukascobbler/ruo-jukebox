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
import {Album} from '../../../models/Album';
import {Artist} from '../../../models/Artist';
import {Router} from '@angular/router';
import {SearchComponent} from '../search/search.component';
import {AuthService} from '../../../services/auth/auth.service';
import {Song} from '../../../models/Song';
import {PlayerService} from '../../../services/player/player.service';

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
  playerService = inject(PlayerService);

  albums: Album[] = [];

  artists: Artist[] = [];

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

  getArtists(item: Album | Song) {
    return item.artists.map(a => a.name).join(" ")
  }
}
