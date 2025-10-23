import {Component, inject, OnInit} from '@angular/core';
import {
    BoxMissingIconXLargeComponent
} from "../../../common/missing-icons/box/missing-icon-x-large/box-missing-icon-x-large.component";
import {NgClass, NgForOf, NgIf} from "@angular/common";
import {ReactiveFormsModule} from "@angular/forms";
import {Album} from '../../../../models/album/Album';
import {Artist} from '../../../../models/Artist';
import {
  RoundMissingIconSmallComponent
} from '../../../common/missing-icons/round/round-missing-icon-small/round-missing-icon-small.component';
import {Song} from '../../../../models/Song';
import {ActivatedRoute, Router} from '@angular/router';
import {AuthService} from '../../../../services/auth/auth.service';
import {ArtistsService} from '../../../../services/artists/artists.service';
import {ToastrService} from '../../../../services/toastr/toastr.service';
import {MatProgressSpinner} from '@angular/material/progress-spinner';

@Component({
  selector: 'app-artist',
  standalone: true,
  imports: [
    BoxMissingIconXLargeComponent,
    NgForOf,
    ReactiveFormsModule,
    RoundMissingIconSmallComponent,
    NgClass,
    MatProgressSpinner,
    NgIf
  ],
  templateUrl: './artist.component.html',
  styleUrl: './artist.component.scss'
})
export class ArtistComponent implements OnInit {
  router = inject(Router);
  route = inject(ActivatedRoute);
  artistsService = inject(ArtistsService);
  toast = inject(ToastrService);
  auth = inject(AuthService);

  loading = true;
  artist: Artist | null = null;
  artistId: string = "";

  ngOnInit() {
    this.artistId = this.route.snapshot.params['id'];

    this.artistsService.get(this.artistId).subscribe({
      next: value => {
        this.loading = false;
        this.artist = value;

        setTimeout(() => this.applyHorizontalScrolling(), 100);
      },
      error: err => {
        this.toast.error("Error", "Error loading artist: " + err);
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
}
