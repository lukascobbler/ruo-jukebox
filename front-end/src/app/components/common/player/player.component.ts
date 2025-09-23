import {Component, inject} from '@angular/core';
import {NgClass, NgForOf} from '@angular/common';
import {BoxMissingIconSmallComponent} from '../missing-icons/box/missing-icon-small/box-missing-icon-small.component';
import {MatDialog} from '@angular/material/dialog';
import {LyricsDialogComponent} from '../dialogs/lyrics/lyrics-dialog.component';
import {Song} from '../../../models/Song';

@Component({
  selector: 'app-player',
  standalone: true,
  imports: [
    NgForOf,
    NgClass,
    BoxMissingIconSmallComponent
  ],
  templateUrl: './player.component.html',
  styleUrl: './player.component.scss'
})
export class PlayerComponent {
  dialog = inject(MatDialog);

  ratings = [1, 2, 3];
  starRating = 2;
  hoverRating = 0;
  currentlyPlayingSong: Song = { id: '1', no: 1, title: 'Title', album: 'Album', albumId: '1', duration: 420, artist: 'Awesome Artist 123', artistId: '1', lyrics: 'No lyrics found' }

  updateProgress(event: Event) {
    const input = event.target as HTMLInputElement;
    const value = input.value;
    input.style.setProperty('--value', value + '%');
  }

  setStarRating(starRating: number) {
    this.starRating = starRating;
  }

  setHoverRating(rating: number) {
    this.hoverRating = rating;
  }

  resetHoverRating() {
    this.hoverRating = 0;
  }

  openLyrics() {
    this.dialog.open(LyricsDialogComponent, {
      width: '600px',
      maxWidth: '70vw',
      data: { lyrics: this.currentlyPlayingSong.lyrics }
    });
  }
}
