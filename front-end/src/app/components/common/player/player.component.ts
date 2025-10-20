import {Component, inject, OnInit, OnDestroy} from '@angular/core';
import {NgClass, NgForOf, NgIf} from '@angular/common';
import {BoxMissingIconSmallComponent} from '../missing-icons/box/missing-icon-small/box-missing-icon-small.component';
import {MatDialog} from '@angular/material/dialog';
import {LyricsDialogComponent} from '../dialogs/lyrics/lyrics-dialog.component';
import {PlayerService} from '../../../services/player/player.service';
import {Subscription, interval} from 'rxjs';
import {Song} from '../../../models/Song';
import {Artist} from '../../../models/Artist';
import {Role} from '../../../models/Role';

@Component({
  selector: 'app-player',
  standalone: true,
  imports: [NgForOf, NgClass, BoxMissingIconSmallComponent, NgIf],
  templateUrl: './player.component.html',
  styleUrl: './player.component.scss'
})
export class PlayerComponent implements OnInit, OnDestroy {
  dialog = inject(MatDialog);
  protected readonly player = inject(PlayerService);

  currentlyPlayingSong: Song = {
    cover_url: '',
    audio_url: '',
    song_id: '',
    no: 0,
    title: '---',
    album: '',
    albumId: '',
    duration: 0,
    artists: [{name: ''} as Artist],
    artistId: '',
    lyrics: 'No lyrics found',
    genres: []
  };

  progress = 0;
  currentTime = 0;
  duration = 0;
  userRole: Role = 'Admin';
  ratings = [1, 2, 3];
  starRating = 2;
  hoverRating = 0;

  private subs: Subscription[] = [];

  ngOnInit() {
    this.subs.push(
      this.player.currentSong$.subscribe(song => {
        if (song) {
          this.currentlyPlayingSong = song;
          this.duration = song.duration || 0;
        }
      })
    );

    this.subs.push(
      interval(500).subscribe(() => {
        this.currentTime = this.player.getCurrentTime();
        this.duration = this.player.getDuration();
        this.progress = this.player.getProgressPercent();
      })
    );
  }

  ngOnDestroy() {
    this.subs.forEach(s => s.unsubscribe());
  }

  formatTime(seconds: number): string {
    if (!seconds || isNaN(seconds)) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
  }

  togglePlay() {
    this.player.play();
  }

  skipNext() {
    this.player.next();
  }

  skipPrevious() {
    this.player.previous();
  }

  updateProgress(event: Event) {
    const input = event.target as HTMLInputElement;
    const value = Number(input.value);
    input.style.setProperty('--value', value + '%');
    this.player.seekTo(value);
  }

  openLyrics() {
    this.dialog.open(LyricsDialogComponent, {
      width: '600px',
      maxWidth: '70vw',
      data: {lyrics: this.currentlyPlayingSong.lyrics}
    });
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

  getArtistNames(song: Song): string {
    return song.artists.map((a: Artist) => a.name).join(', ') || '';
  }
}
