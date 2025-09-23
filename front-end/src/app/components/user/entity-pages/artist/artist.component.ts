import {Component, inject, OnInit} from '@angular/core';
import {
    BoxMissingIconXLargeComponent
} from "../../../common/missing-icons/box/missing-icon-x-large/box-missing-icon-x-large.component";
import {NgClass, NgForOf} from "@angular/common";
import {ReactiveFormsModule} from "@angular/forms";
import {Album} from '../../../../models/Album';
import {Artist} from '../../../../models/Artist';
import {
  RoundMissingIconSmallComponent
} from '../../../common/missing-icons/round/round-missing-icon-small/round-missing-icon-small.component';
import {Song} from '../../../../models/Song';
import {Router} from '@angular/router';

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

  artist: Artist = {id: '', name: 'Awesome artist', isSubscribed: true};

  singles: Song[] = [
    { id: '1', no: 1, title: 'Title', album: 'Album', albumId: '1', duration: 420, artist: 'Awesome Artist 123', artistId: '1' },
    { id: '2', no: 1, title: 'Title', album: 'Album', albumId: '2', duration: 420, artist: 'Awesome Artist 123', artistId: '2' },
    { id: '3', no: 1, title: 'Title', album: 'Album', albumId: '3', duration: 420, artist: 'Awesome Artist 123', artistId: '3' },
    { id: '4', no: 1, title: 'Title', album: 'Album', albumId: '4', duration: 420, artist: 'Awesome Artist 123', artistId: '4' },
    { id: '5', no: 1, title: 'Title', album: 'Album', albumId: '5', duration: 420, artist: 'Awesome Artist 123', artistId: '5' },
    { id: '6', no: 1, title: 'Title', album: 'Album', albumId: '6', duration: 420, artist: 'Awesome Artist 123', artistId: '6' },
    { id: '7', no: 1, title: 'Title', album: 'Album', albumId: '7', duration: 420, artist: 'Awesome Artist 123', artistId: '7' },
    { id: '8', no: 1, title: 'Title', album: 'Album', albumId: '8', duration: 420, artist: 'Awesome Artist 123', artistId: '8' },
    { id: '9', no: 1, title: 'Title', album: 'Album', albumId: '9', duration: 420, artist: 'Awesome Artist 123', artistId: '9' },
  ];

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
