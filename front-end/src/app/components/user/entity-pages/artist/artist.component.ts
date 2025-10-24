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
import {Genre} from '../../../../models/Genre';
import {firstValueFrom} from 'rxjs';
import {SubscriptionsService} from '../../../../services/subscriptions/subscriptions.service';
import {PlayerService} from '../../../../services/player/player.service';

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
  subsService = inject(SubscriptionsService);
  toast = inject(ToastrService);
  auth = inject(AuthService);
  playerService = inject(PlayerService);

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

  private extractError(err: any): string {
    const msg =
      err?.error?.error ||
      err?.error?.message ||
      err?.message ||
      'Unexpected error. Please try again.';
    return typeof msg === 'string' ? msg : 'Unexpected error. Please try again.';
  }

  async toggleArtistSubscription(event: Event) {
    event.stopPropagation();

    const topic = this.artist!.artist_id;
    const prev = !!this.artist!.isSubscribed;

    this.artist!.isSubscribed = !prev;

    try {
      if (prev) {
        await firstValueFrom(this.subsService.delete(topic, null,[topic],[],null));
      } else {
        await firstValueFrom(this.subsService.create(topic, null,[topic],[],null));
      }
      this.toast.success(prev ? 'Unsubscribed' : 'Subscribed', this.artist!.name);
    } catch (err: any) {
      this.artist!.isSubscribed = prev;
      const msg = this.extractError(err);
      this.toast.error(prev ? 'Unsubscribe error' : 'Subscribe error', msg);
    }
  }
}
