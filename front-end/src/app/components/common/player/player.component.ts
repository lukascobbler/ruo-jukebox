import { Component } from '@angular/core';
import {NgClass, NgForOf} from '@angular/common';
import {BoxMissingIconSmallComponent} from '../missing-icons/box/missing-icon-small/box-missing-icon-small.component';

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
  ratings = [1, 2, 3];
  starRating = 2;
  hoverRating = 0;

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
}
