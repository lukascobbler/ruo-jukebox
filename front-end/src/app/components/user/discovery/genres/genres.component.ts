import {Component, inject, OnInit} from '@angular/core';
import {NgClass, NgForOf} from "@angular/common";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {GenreItem} from '../../../../models/GenreItem';
import {Router} from '@angular/router';
import {SearchComponent} from '../../search/search.component';
import {AuthService} from '../../../../services/auth/auth.service';
import { GenresService } from '../../../../services/genres/genres.service';
import { ToastrService } from '../../../../services/toastr/toastr.service';
import { SubscriptionsService } from '../../../../services/subscriptions/subscriptions.service';
import { map } from 'rxjs/operators';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-genres',
  standalone: true,
  imports: [
    NgForOf,
    ReactiveFormsModule,
    FormsModule,
    NgClass,
    SearchComponent,
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
  genres: GenreItem[] = [];
  busyIds = new Set<string>();

  ngOnInit(): void {
    this.fetchGenres();
  }

  private fetchGenres(): void {
    this.genresService.list().subscribe({
      next: (items) => {
        console.log(items)
        this.genres = items ?? [];
      },
      error: (err) => {
        console.error('Failed to load genres', err);
        const msg = this.extractError(err);
        this.toast.error('Genres error', msg);
      }
    });
  }

  goToGenre(genre: GenreItem) {
    this.router.navigate(['genre', genre.genre_id]);
  }

  unsubscribeFromGenre(event: Event, genre: GenreItem) {
    event.stopPropagation();

    genre.isSubscribed = !genre.isSubscribed;
  }
    private extractError(err: any): string {
    const msg =
      err?.error?.error ||
      err?.error?.message ||
      err?.message ||
      'Unexpected error. Please try again.';
    return typeof msg === 'string' ? msg : 'Unexpected error. Please try again.';
  }

async toggleGenreSubscription(event: Event, genre: GenreItem) {
  event.stopPropagation();
  if (this.busyIds.has(genre.genre_id)) return;

  const topic = genre.genre_id;
  const prev = !!genre.isSubscribed;

  genre.isSubscribed = !prev;
  this.busyIds.add(genre.genre_id);

  try {
    if (prev) {
      await firstValueFrom(this.subsService.delete(topic));
    } else {
      await firstValueFrom(this.subsService.create(topic));
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
