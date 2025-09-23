import { Component } from '@angular/core';
import {
  MatCell,
  MatCellDef,
  MatColumnDef,
  MatHeaderCell, MatHeaderCellDef,
  MatHeaderRow,
  MatHeaderRowDef,
  MatRow, MatRowDef, MatTable
} from "@angular/material/table";
import {MatIconButton} from "@angular/material/button";
import {Artist} from '../../../models/Artist';

@Component({
  selector: 'app-all-artists',
  standalone: true,
  imports: [
    MatCell,
    MatCellDef,
    MatColumnDef,
    MatHeaderCell,
    MatHeaderRow,
    MatHeaderRowDef,
    MatIconButton,
    MatRow,
    MatRowDef,
    MatTable,
    MatHeaderCellDef
  ],
  templateUrl: './all-artists.component.html',
  styleUrl: './all-artists.component.scss'
})
export class AllArtistsComponent {
  displayedColumns = ['name', 'genres', 'biography', 'actions'];
  artistsDataSource: Artist[] = [
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
  ];

  getArtistGenres(artist: Artist) {
    return artist.genres.map(g => g['name']).join(', ');
  }
}
