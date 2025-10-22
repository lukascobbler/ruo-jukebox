import {Component, inject, OnInit} from '@angular/core';
import {NgClass, NgForOf, NgIf} from "@angular/common";
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
import {MatProgressSpinner} from '@angular/material/progress-spinner';

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
  private router = inject(Router);
  auth = inject(AuthService);
  toast = inject(ToastrService);
  loading = true;
  genres: GenreItem[] = [];

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

  goToGenre(genre: GenreItem) {
    this.router.navigate(['genre', genre.genre_id]);
  }
}
