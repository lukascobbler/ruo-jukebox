import {Component, inject, OnInit} from '@angular/core';
import {NgForOf, NgIf} from '@angular/common';
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
import { FeedService } from '../../../services/feed/feed.service';
import { ToastrService } from '../../../services/toastr/toastr.service';
import {MatProgressSpinner} from '@angular/material/progress-spinner';

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
    SearchComponent,
    NgIf,
    MatProgressSpinner
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  router = inject(Router);
  auth = inject(AuthService);
  playerService = inject(PlayerService);
  feedService = inject(FeedService);
  albums: Album[] = [];
  songs: Song[] = []
  artists: Artist[] = [];
  loading = true;
  toast = inject(ToastrService)
  ngOnInit() {
    this.feedService.get().subscribe({
      next: value => {
        this.songs = value.songs;
        this.artists = value.artists
        this.albums = value.albums
        this.loading = false;
        setTimeout(() => this.applyHorizontalBarScrolling(), 100)
      },
      error: err => {
        this.toast.error("Error", "Error loading feed: " + err);
      }
    })
  }

  getArtists(item: Album | Song) {
    return item.artists.map(a => a.name).join(" ")
  }

  applyHorizontalBarScrolling() {
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
