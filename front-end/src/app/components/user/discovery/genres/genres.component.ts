import {Component, inject} from '@angular/core';
import {NgClass, NgForOf} from "@angular/common";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {GenreItem} from '../../../../models/GenreItem';
import {Router} from '@angular/router';
import {SearchComponent} from '../../search/search.component';
import {AuthService} from '../../../../services/auth/auth.service';

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
export class GenresComponent {
  private router = inject(Router);
  auth = inject(AuthService);

  genres: GenreItem[] = [
    { name: 'Rock', isSubscribed: true, id: '1' },
    { name: 'Jazz', isSubscribed: false, id: '2' },
    { name: 'Classical', isSubscribed: false, id: '3' },
    { name: 'Country', isSubscribed: false, id: '4' },
    { name: 'Soul', isSubscribed: true, id: '5' },
    { name: 'Pop', isSubscribed: false, id: '6' },
    { name: 'Blues', isSubscribed: true, id: '7' },
    { name: 'Hip-Hop', isSubscribed: false, id: '8' },
    { name: 'Reggae', isSubscribed: false, id: '9' },
    { name: 'Latin', isSubscribed: false, id: '10' },
    { name: 'Funk', isSubscribed: true, id: '11' },
    { name: 'Electronic', isSubscribed: false, id: '12' },
  ];

  goToGenre(genre: GenreItem) {
    this.router.navigate(['genre', genre.id]);
  }

  unsubscribeFromGenre(event: Event, genre: GenreItem) {
    event.stopPropagation();

    genre.isSubscribed = !genre.isSubscribed;
  }
}
