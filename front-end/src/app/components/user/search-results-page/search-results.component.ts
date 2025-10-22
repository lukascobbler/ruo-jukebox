import {Component, DestroyRef, inject, OnInit} from '@angular/core';
import {NgForOf, NgIf} from "@angular/common";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {ActivatedRoute, Router} from '@angular/router';
import {Album} from '../../../models/album/Album';
import {Artist} from '../../../models/Artist';
import {Song} from '../../../models/Song';
import {
  BoxMissingIconLargeComponent
} from '../../common/missing-icons/box/missing-icon-large/box-missing-icon-large.component';
import {
  RoundMissingIconLargeComponent
} from '../../common/missing-icons/round/round-missing-icon-large/round-missing-icon-large.component';
import {SearchComponent} from '../search/search.component';
import {AuthService} from '../../../services/auth/auth.service';
import { ArtistsService } from '../../../services/artists/artists.service';
import { ToastrService } from '../../../services/toastr/toastr.service';
import { map, of, switchMap } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-search-results-page',
  standalone: true,
  imports: [
    NgForOf,
    NgIf,
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
  auth = inject(AuthService);
  private artistsService = inject(ArtistsService);
  private toast = inject(ToastrService);
  private destroyRef = inject(DestroyRef);

  searchTerm: string = "";

  foundSongs: Song[] = [
    { cover_url: '', audio_url: '', song_id: '1', no: 1, title: 'Title', album: 'Album', albumId: '1', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '1', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    { cover_url: '', audio_url: '', song_id: '2', no: 1, title: 'Title', album: 'Album', albumId: '2', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '2', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    { cover_url: '', audio_url: '', song_id: '3', no: 1, title: 'Title', album: 'Album', albumId: '3', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '3', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    { cover_url: '', audio_url: '', song_id: '4', no: 1, title: 'Title', album: 'Album', albumId: '4', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '4', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    { cover_url: '', audio_url: '', song_id: '5', no: 1, title: 'Title', album: 'Album', albumId: '5', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '5', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    { cover_url: '', audio_url: '', song_id: '6', no: 1, title: 'Title', album: 'Album', albumId: '6', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '6', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    { cover_url: '', audio_url: '', song_id: '7', no: 1, title: 'Title', album: 'Album', albumId: '7', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '7', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    { cover_url: '', audio_url: '', song_id: '8', no: 1, title: 'Title', album: 'Album', albumId: '8', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '8', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    { cover_url: '', audio_url: '', song_id: '9', no: 1, title: 'Title', album: 'Album', albumId: '9', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '9', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
  ];

  foundAlbums: Album[] = [
    { id: '1', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '1', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false},
    { id: '2', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '2', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false},
    { id: '3', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '3', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false},
    { id: '4', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '4', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false},
    { id: '5', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '5', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false},
    { id: '6', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '6', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false},
    { id: '7', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '7', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false},
    { id: '8', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '8', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false},
    { id: '9', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '9', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false},
    { id: '10', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '10', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false},
  ];

  foundArtists: Artist[] = [];

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


    this.route.paramMap.pipe(
      map(pm => (pm.get('query') || '').trim()),
      takeUntilDestroyed(this.destroyRef),
      switchMap(q => {
        this.searchTerm = q;
        if (!q) {
          this.foundArtists = [];
          return of<Artist[]>([]);
        }
        return this.artistsService.searchByName(q);
      })
    ).subscribe({
      next: (artists) => {
        this.foundArtists = (artists || []).map(a => ({
          id: a.id,
          name: a.name,
          biography: a.biography,
          genres: a.genres,
          pictureUrl: a.pictureUrl ?? null,
          pictureKey: null
        }));
      },
      error: (err) => {
        const msg =
          err?.error?.error ||
          err?.error?.message ||
          err?.message ||
          'Unexpected error. Please try again.';
        this.toast.error('Search artists error', msg);
        this.foundArtists = [];
      }
    });


    this.searchTerm = this.route.snapshot.params['query'];
  }
}
