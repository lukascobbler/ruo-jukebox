import { Component, inject, OnInit } from '@angular/core';
import {
  MatCell,
  MatCellDef,
  MatColumnDef,
  MatHeaderCell,
  MatHeaderCellDef,
  MatHeaderRow,
  MatHeaderRowDef,
  MatRow,
  MatRowDef,
  MatTable,
} from '@angular/material/table';
import { MatIconButton } from '@angular/material/button';
import { Artist } from '../../../models/Artist';
import {
  MatDialog,
  MatDialogModule,
  MatDialogRef,
} from '@angular/material/dialog';
import { CreateArtistDialogComponent } from '../dialogs/artist/create-artist-dialog.component';
import { GenresService } from '../../../services/genres/genres.service';
import { ToastrService } from '../../../services/toastr/toastr.service';
import { GenreItem } from '../../../models/GenreItem';

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
    MatHeaderCellDef,
    MatDialogModule,
  ],
  templateUrl: './all-artists.component.html',
  styleUrl: './all-artists.component.scss',
})
export class AllArtistsComponent implements OnInit {
  dialog = inject(MatDialog);
  displayedColumns = ['name', 'genres', 'biography', 'actions'];
  private genresService = inject(GenresService);
  private toast = inject(ToastrService);
  artistsDataSource: Artist[] = [
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
    {
      id: '1',
      name: 'Awesome artist',
      genres: [
        { id: '1', name: 'jazz' },
        { id: '2', name: 'country' },
        { id: '3', name: 'rock' },
      ],
      biography:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non ante nisi. Duis luctus purus at quam cursus lobortis.',
    },
  ];

  genres: GenreItem[] = [];

  ngOnInit(): void {
    this.fetchGenres();
  }

  private fetchGenres(): void {
    this.genresService.list().subscribe({
      next: (items) => {
        this.genres = items ?? [];
      },
      error: (err) => {
        console.error('Failed to load genres', err);
        const msg = this.extractError(err);
        this.toast.error('Genres error', msg);
      },
    });
  }

  getArtistGenres(artist: Artist) {
    return artist.genres.map((g) => g['name']).join(', ');
  }

  createNewArtist() {
    const ref = this.dialog.open(CreateArtistDialogComponent, {
      width: '400px',
      minWidth: '40vw',
    });

    ref.componentInstance.genres = this.genres;
  }
  private extractError(err: any): string {
    const msg =
      err?.error?.error ||
      err?.error?.message ||
      err?.message ||
      'Unexpected error. Please try again.';
    return typeof msg === 'string'
      ? msg
      : 'Unexpected error. Please try again.';
  }
}
