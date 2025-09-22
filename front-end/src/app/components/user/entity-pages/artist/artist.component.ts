import {Component, OnInit} from '@angular/core';
import {
    BoxMissingIconXLargeComponent
} from "../../../common/missing-icons/box/missing-icon-x-large/box-missing-icon-x-large.component";
import {MatFormField, MatSuffix} from "@angular/material/form-field";
import {MatInput} from "@angular/material/input";
import {NgClass, NgForOf} from "@angular/common";
import {ReactiveFormsModule} from "@angular/forms";
import {
    RoundMissingIconXLargeComponent
} from "../../../common/missing-icons/round/round-missing-icon-x-large/round-missing-icon-x-large.component";
import {Album} from '../../../../models/Album';
import {Artist} from '../../../../models/Artist';
import {
  BoxMissingIconSmallComponent
} from '../../../common/missing-icons/box/missing-icon-small/box-missing-icon-small.component';
import {
  RoundMissingIconSmallComponent
} from '../../../common/missing-icons/round/round-missing-icon-small/round-missing-icon-small.component';
import {Song} from '../../../../models/Song';

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
  artist: Artist = {id: '', name: 'Awesome artist', isSubscribed: true};

  singles: Song[] = [
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
    { id: '', title: 'Awesome song', album: 'Album', albumId: '', duration: 420, artist: 'Awesome artist 1, Artist Awesome 2', artistId: '' },
  ];

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
