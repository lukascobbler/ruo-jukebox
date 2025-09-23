import {Component, inject, OnInit} from '@angular/core';
import {NgForOf} from "@angular/common";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {ActivatedRoute, Router} from '@angular/router';
import {Album} from '../../../models/Album';
import {ArtistUserView} from '../../../models/ArtistUserView';
import {Song} from '../../../models/Song';
import {
  BoxMissingIconLargeComponent
} from '../../common/missing-icons/box/missing-icon-large/box-missing-icon-large.component';
import {
  RoundMissingIconLargeComponent
} from '../../common/missing-icons/round/round-missing-icon-large/round-missing-icon-large.component';
import {SearchComponent} from '../search/search.component';

@Component({
  selector: 'app-search-results-page',
  standalone: true,
  imports: [
    NgForOf,
    ReactiveFormsModule,
    FormsModule,
    BoxMissingIconLargeComponent,
    RoundMissingIconLargeComponent,
    SearchComponent
  ],
  templateUrl: './search-results.component.html',
  styleUrl: './search-results.component.scss'
})
export class SearchResultsComponent implements OnInit {
  router = inject(Router);
  route = inject(ActivatedRoute);

  searchTerm: string = "";

  foundSongs: Song[] = [
    { id: '1', no: 1, title: 'Title', album: 'Album', albumId: '1', duration: 420, artist: 'Awesome Artist 123', artistId: '1', lyrics: 'No lyrics found' },
    { id: '2', no: 1, title: 'Title', album: 'Album', albumId: '2', duration: 420, artist: 'Awesome Artist 123', artistId: '2', lyrics: 'No lyrics found' },
    { id: '3', no: 1, title: 'Title', album: 'Album', albumId: '3', duration: 420, artist: 'Awesome Artist 123', artistId: '3', lyrics: 'No lyrics found' },
    { id: '4', no: 1, title: 'Title', album: 'Album', albumId: '4', duration: 420, artist: 'Awesome Artist 123', artistId: '4', lyrics: 'No lyrics found' },
    { id: '5', no: 1, title: 'Title', album: 'Album', albumId: '5', duration: 420, artist: 'Awesome Artist 123', artistId: '5', lyrics: 'No lyrics found' },
    { id: '6', no: 1, title: 'Title', album: 'Album', albumId: '6', duration: 420, artist: 'Awesome Artist 123', artistId: '6', lyrics: 'No lyrics found' },
    { id: '7', no: 1, title: 'Title', album: 'Album', albumId: '7', duration: 420, artist: 'Awesome Artist 123', artistId: '7', lyrics: 'No lyrics found' },
    { id: '8', no: 1, title: 'Title', album: 'Album', albumId: '8', duration: 420, artist: 'Awesome Artist 123', artistId: '8', lyrics: 'No lyrics found' },
    { id: '9', no: 1, title: 'Title', album: 'Album', albumId: '9', duration: 420, artist: 'Awesome Artist 123', artistId: '9', lyrics: 'No lyrics found' },
  ];

  foundAlbums: Album[] = [
    {id: '1', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '2', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '3', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '4', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '5', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '6', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '7', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '8', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '9', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
    {id: '10', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein'},
  ];

  foundArtists: ArtistUserView[] = [
    {id: '1', name: 'Awesome artist', isSubscribed: false},
    {id: '2', name: 'Awesome artist', isSubscribed: false},
    {id: '3', name: 'Awesome artist', isSubscribed: false},
    {id: '4', name: 'Awesome artist', isSubscribed: false},
    {id: '5', name: 'Awesome artist', isSubscribed: false},
    {id: '6', name: 'Awesome artist', isSubscribed: false},
    {id: '7', name: 'Awesome artist', isSubscribed: false},
    {id: '8', name: 'Awesome artist', isSubscribed: false},
    {id: '9', name: 'Awesome artist', isSubscribed: false},
    {id: '10', name: 'Awesome artist', isSubscribed: false},
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

    this.searchTerm = this.route.snapshot.params['query'];
  }
}
