import {MatTable, MatCell, MatCellDef, MatColumnDef, MatHeaderCell, MatHeaderCellDef, MatHeaderRow, MatHeaderRowDef, MatRow, MatRowDef} from '@angular/material/table';
import {BoxMissingIconSmallComponent} from '../../common/missing-icons/box/missing-icon-small/box-missing-icon-small.component';
import {CreateSingleDialogComponent} from '../dialogs/single/create-single-dialog.component';
import {MatProgressSpinner} from '@angular/material/progress-spinner';
import {ToastrService} from '../../../services/toastr/toastr.service';
import {PlayerService} from '../../../services/player/player.service';
import {SongsService, SingleItem} from '../../../services/singles/singles.service';
import {MatDialog, MatDialogRef} from '@angular/material/dialog';
import {Component, inject, OnInit} from '@angular/core';
import {MatIconButton} from '@angular/material/button';
import {NgIf} from '@angular/common';
import {lastValueFrom} from 'rxjs';

@Component({
  selector: 'app-all-singles',
  standalone: true,
  imports: [
    BoxMissingIconSmallComponent,
    MatCell, MatCellDef, MatColumnDef,
    MatHeaderCell, MatHeaderCellDef, MatHeaderRow, MatHeaderRowDef,
    MatIconButton, MatRow, MatRowDef, MatTable,
    MatProgressSpinner, NgIf
  ],
  templateUrl: './all-singles.component.html',
  styleUrl: './all-singles.component.scss'
})
export class AllSinglesComponent implements OnInit {
  private readonly songsService = inject(SongsService);
  private readonly player = inject(PlayerService);
  private readonly toast = inject(ToastrService);
  private readonly dialog = inject(MatDialog);

  displayedColumns = ['cover', 'name', 'artists', 'genres', 'actions'];
  singlesDataSource: SingleItem[] = [];
  loading = false;

  ngOnInit() {
    this.loadSingles();
  }

  private loadSingles(): void {
    this.loading = true;
    this.songsService.listSingles().subscribe({
      next: (singles) => {
        console.log(singles);
        this.singlesDataSource = singles;
        this.player.loadPlaylist(singles);
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  createNewSingle() {
    const dialogRef: MatDialogRef<CreateSingleDialogComponent, null> = this.dialog.open(CreateSingleDialogComponent, {
      minWidth: '900px'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadSingles();
        this.toast.success('Success', 'Single successfully created!');
      }
    });
  }

  async deleteSong(single: SingleItem): Promise<void> {
    try {
      await lastValueFrom(this.songsService.deleteSingle(single.content_id));
      this.toast.success('Deleted', 'Single deleted successfully');
      this.loadSingles();
    } catch {
      this.toast.error('Error', 'Failed to delete single');
    }
  }

  updateSong(single: SingleItem): void {
    const dialogRef = this.dialog.open(CreateSingleDialogComponent, {
      minWidth: '900px',
      data: {
        content_id: single.content_id,
        name: single.name,
        cover_url: single.cover_url,
        artists: single.artists?.map(a => a.name) || [],
        genres: single.genres?.map(g => g.name) || []
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadSingles();
        this.toast.success('Updated', 'Single successfully updated!');
      }
    });
  }

  getGenreNames(single: SingleItem): string {
    return single.genres?.map(g => g.name).join(', ') || '';
  }

  getArtistNames(single: SingleItem): string {
    return single.artists?.map(a => a.name).join(', ') || '';
  }

  playSong(single: SingleItem): void {
    this.player.play(single);
  }
}
