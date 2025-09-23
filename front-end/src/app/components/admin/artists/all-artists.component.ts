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
import {ArtistAdminView} from '../../../models/ArtistAdminView';

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
  artistsDataSource: ArtistAdminView[] = [
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
    {id: '1', name: 'Awesome artist', genres: ['jazz', 'country', 'rock'], biography: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.'},
  ];
}
