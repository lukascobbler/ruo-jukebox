import {Component, inject} from '@angular/core';
import {MatFormField, MatSuffix} from "@angular/material/form-field";
import {MatInput} from "@angular/material/input";
import {NgClass, NgForOf} from "@angular/common";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {Genre} from '../../../../models/Genre';
import {Router} from '@angular/router';

@Component({
  selector: 'app-genres',
  standalone: true,
  imports: [
    MatFormField,
    MatInput,
    MatSuffix,
    NgForOf,
    ReactiveFormsModule,
    FormsModule,
    NgClass,
  ],
  templateUrl: './genres.component.html',
  styleUrl: './genres.component.scss'
})
export class GenresComponent {
  private router = inject(Router);

  searchTerm: string = "";
  genres: Genre[] = [
    { name: 'Rock', isSubscribed: true, id: '' },
    { name: 'Jazz', isSubscribed: false, id: '' },
    { name: 'Classical', isSubscribed: false, id: '' },
    { name: 'Country', isSubscribed: false, id: '' },
    { name: 'Soul', isSubscribed: true, id: '' },
    { name: 'Pop', isSubscribed: false, id: '' },
    { name: 'Blues', isSubscribed: true, id: '' },
    { name: 'Hip-Hop', isSubscribed: false, id: '' },
    { name: 'Reggae', isSubscribed: false, id: '' },
    { name: 'Latin', isSubscribed: false, id: '' },
    { name: 'Funk', isSubscribed: true, id: '' },
    { name: 'Electronic', isSubscribed: false, id: '' },
  ];

  goToGenre(genre: Genre) {
    this.router.navigate(['genre', genre.id]);
  }
}
