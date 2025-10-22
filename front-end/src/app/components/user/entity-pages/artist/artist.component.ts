import {Component, inject, OnInit} from '@angular/core';
import {
    BoxMissingIconXLargeComponent
} from "../../../common/missing-icons/box/missing-icon-x-large/box-missing-icon-x-large.component";
import {NgClass, NgForOf} from "@angular/common";
import {ReactiveFormsModule} from "@angular/forms";
import {Album} from '../../../../models/album/Album';
import {Artist} from '../../../../models/Artist';
import {
  RoundMissingIconSmallComponent
} from '../../../common/missing-icons/round/round-missing-icon-small/round-missing-icon-small.component';
import {Song} from '../../../../models/Song';
import {Router} from '@angular/router';
import {AuthService} from '../../../../services/auth/auth.service';

@Component({
  selector: 'app-artist',
  standalone: true,
  imports: [
    BoxMissingIconXLargeComponent,
    NgForOf,
    ReactiveFormsModule,
    RoundMissingIconSmallComponent,
    NgClass
  ],
  templateUrl: './artist.component.html',
  styleUrl: './artist.component.scss'
})
export class ArtistComponent implements OnInit {
  router = inject(Router);
  auth = inject(AuthService);

  artist: Artist = {artist_id: '', name: 'Awesome artist', biography: '', genres: [], isSubscribed: true, cover_key: null, cover_url: null};

  singles: Song[] = [
    {cover_url: '', audio_url: '',  song_id: '1', no: 1, title: 'Title', album: 'Album', albumId: '1', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '1', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    {cover_url: '', audio_url: '',  song_id: '2', no: 1, title: 'Title', album: 'Album', albumId: '2', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '2', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    {cover_url: '', audio_url: '',  song_id: '3', no: 1, title: 'Title', album: 'Album', albumId: '3', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '3', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    {cover_url: '', audio_url: '',  song_id: '4', no: 1, title: 'Title', album: 'Album', albumId: '4', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '4', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    {cover_url: '', audio_url: '',  song_id: '5', no: 1, title: 'Title', album: 'Album', albumId: '5', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '5', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    {cover_url: '', audio_url: '',  song_id: '6', no: 1, title: 'Title', album: 'Album', albumId: '6', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '6', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    {cover_url: '', audio_url: '',  song_id: '7', no: 1, title: 'Title', album: 'Album', albumId: '7', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '7', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    {cover_url: '', audio_url: '',  song_id: '8', no: 1, title: 'Title', album: 'Album', albumId: '8', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '8', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
    {cover_url: '', audio_url: '',  song_id: '9', no: 1, title: 'Title', album: 'Album', albumId: '9', duration: 420, artists: [{name: 'Awesome Artist 123'} as Artist], artistId: '9', lyrics: 'No lyrics found', genres: [{genre_id: '1', name: 'rock'}, {genre_id: '1', name: 'jazz'}, {genre_id: '1', name: 'conutry'}] },
  ];

  albums: Album[] = [
    { id: '1', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '1', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false },
    { id: '2', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '2', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false },
    { id: '3', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '3', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false },
    { id: '4', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '4', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false },
    { id: '5', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '5', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false },
    { id: '6', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '6', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false },
    { id: '7', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '7', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false },
    { id: '8', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '8', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false },
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
