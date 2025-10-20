import {Component, inject, OnInit} from '@angular/core';
import {NgForOf, NgIf} from "@angular/common";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {
  BoxMissingIconXLargeComponent
} from '../../../common/missing-icons/box/missing-icon-x-large/box-missing-icon-x-large.component';
import {
  RoundMissingIconXLargeComponent
} from '../../../common/missing-icons/round/round-missing-icon-x-large/round-missing-icon-x-large.component';
import {Album} from '../../../../models/Album';
import {Artist} from '../../../../models/Artist';
import {ActivatedRoute, Router} from '@angular/router';
import {SearchComponent} from '../../search/search.component';
import {Genre} from '../../../../models/Genre';
import {AuthService} from '../../../../services/auth/auth.service';
import { map, switchMap } from 'rxjs';
import { ToastrService } from '../../../../services/toastr/toastr.service';
import { ArtistsService } from '../../../../services/artists/artists.service';

@Component({
  selector: 'app-music-content',
  standalone: true,
  imports: [
    NgForOf,
    ReactiveFormsModule,
    FormsModule,
    BoxMissingIconXLargeComponent,
    RoundMissingIconXLargeComponent,
    SearchComponent,
    NgIf
  ],
  templateUrl: './music-content.component.html',
  styleUrl: './music-content.component.scss'
})
export class MusicContentComponent implements OnInit {
  router = inject(Router);
  route = inject(ActivatedRoute);
  auth = inject(AuthService);
  toast = inject(ToastrService);
  private artistsService = inject(ArtistsService);
  genre: Genre | null  = null;

  albums: Album[] = [
    { id: '1', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}] },
    { id: '2', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '2', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}] },
    { id: '3', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '3', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}] },
    { id: '4', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '4', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}] },
    { id: '5', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '5', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}] },
    { id: '6', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '6', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}] },
    { id: '7', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '7', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}] },
    { id: '8', name: 'Awesome album', artist: 'Awesome Artist 1 Albert Einstein', artistId: '8', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}] },
  ];

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
    
    this.route.paramMap.pipe(
      switchMap(pm => {
        const genreId = pm.get('id');
        if (genreId) {
          // with images
          return this.artistsService.getByGenre(genreId).pipe(
            map((list: Artist[]) =>
              list.map(a => ({
                id: a.id,
                name: a.name,
                biography: a.biography,
                genres: a.genres,
                pictureUrl: a.pictureUrl ?? null,
                pictureKey: null
              }))
            )
          );
        }
        // all artists (no images)
        return this.artistsService.getAll().pipe(
          map(list =>
            list.map(a => ({
              ...a,
              pictureUrl: null,
              pictureKey: null
            }))
          )
        );
      })
    ).subscribe({
      next: (artists) => { this.artists = artists ?? []; },
      error: (err) => {
        const msg = this.extractError(err);
        this.toast.error('Artists error', msg);
      }
    });
    let genreId = this.route.snapshot.params['id'];
  }
    private extractError(err: any): string {
    const msg =
      err?.error?.error ||
      err?.error?.message ||
      err?.message ||
      'Unexpected error. Please try again.';
    return typeof msg === 'string' ? msg : 'Unexpected error. Please try again.';
  }
}
