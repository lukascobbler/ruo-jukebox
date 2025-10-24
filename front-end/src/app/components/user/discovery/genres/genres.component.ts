import {Component, inject, OnInit} from '@angular/core';
import {NgClass, NgForOf, NgIf} from "@angular/common";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {Genre} from '../../../../models/Genre';
import {Router} from '@angular/router';
import {SearchComponent} from '../../search/search.component';
import {AuthService} from '../../../../services/auth/auth.service';
import { GenresService } from '../../../../services/genres/genres.service';
import { ToastrService } from '../../../../services/toastr/toastr.service';
import { SubscriptionsService } from '../../../../services/subscriptions/subscriptions.service';
import { firstValueFrom } from 'rxjs';
import {MatProgressSpinner} from '@angular/material/progress-spinner';
import {PlayerService} from '../../../../services/player/player.service';

@Component({
  selector: 'app-genres',
  standalone: true,
  imports: [
    NgForOf,
    ReactiveFormsModule,
    FormsModule,
    NgClass,
    SearchComponent,
    MatProgressSpinner,
    NgIf,
  ],
  templateUrl: './genres.component.html',
  styleUrl: './genres.component.scss'
})
export class GenresComponent implements OnInit {
  private genresService = inject(GenresService);
  private subsService = inject(SubscriptionsService);
  private router = inject(Router);
  auth = inject(AuthService);
  toast = inject(ToastrService);
  playerService = inject(PlayerService);
  loading = true;
  genres: Genre[] = [];
  busyIds = new Set<string>();

  ngOnInit(): void {
    this.fetchGenres();
  }

  private fetchGenres(): void {
    this.genresService.list().subscribe({
      next: (items) => {
        this.genres = items ?? [];
        this.loading = false;
      },
      error: (err) => {
        this.toast.error("Error", 'Failed to load genres', err);
        this.loading = false;
      }
    });
  }

  goToGenre(genre: Genre) {
    this.router.navigate(['genre', genre.genre_id]);
  }

  private extractError(err: any): string {
    const msg =
      err?.error?.error ||
      err?.error?.message ||
      err?.message ||
      'Unexpected error. Please try again.';
    return typeof msg === 'string' ? msg : 'Unexpected error. Please try again.';
  }

  async toggleGenreSubscription(event: Event, genre: Genre) {
    event.stopPropagation();
    if (this.busyIds.has(genre.genre_id)) return;
    const topic = genre.genre_id;
    const prev = !!genre.isSubscribed;

    genre.isSubscribed = !prev;
    this.busyIds.add(genre.genre_id);

    try {
      if (prev) {
        await firstValueFrom(this.subsService.delete(topic, null,[],[topic],null));
      } else {
        await firstValueFrom(this.subsService.create(topic, null,[],[topic],null));
      }
      this.toast.success(prev ? 'Unsubscribed' : 'Subscribed', genre.name);
    } catch (err: any) {
      genre.isSubscribed = prev;
      const msg = this.extractError(err);
      this.toast.error(prev ? 'Unsubscribe error' : 'Subscribe error', msg);
    } finally {
      this.busyIds.delete(genre.genre_id);
    }
  }
}
