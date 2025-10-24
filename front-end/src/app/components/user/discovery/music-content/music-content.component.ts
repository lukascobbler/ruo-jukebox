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
import {GenresService} from '../../../../services/genres/genres.service';
import {MatProgressSpinner} from '@angular/material/progress-spinner';

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
    NgIf,
    MatProgressSpinner
  ],
  templateUrl: './music-content.component.html',
  styleUrl: './music-content.component.scss'
})
export class MusicContentComponent implements OnInit {
  router = inject(Router);
  route = inject(ActivatedRoute);
  auth = inject(AuthService);
  toast = inject(ToastrService);
  genresService = inject(GenresService);
  loading = true;

  genre: Genre | null  = null;

  ngOnInit() {
    let genreId = this.route.snapshot.params['id'];

    this.genresService.get(genreId).subscribe({
      next: value => {
        this.genre = value;
        this.loading = false;
        setTimeout(() => this.applyHorizontalScrolling(), 100);
      },
      error: err => {
        this.toast.error("Error", "Error loading music content for genres: " + err)
        this.loading = false;
      }
    })
  }

  applyHorizontalScrolling() {
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

  getArtists(item: Album) {
    return item.artists.map(a => a.name).join(" ")
  }
}
