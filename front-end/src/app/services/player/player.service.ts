import {inject, Injectable} from '@angular/core';
import {BehaviorSubject} from 'rxjs';
import {Song} from '../../models/Song';
import { SongCacheService } from '../song-cache/song-cache.service';

@Injectable({providedIn: 'root'})
export class PlayerService {
  private audio = new Audio();
  private playlist: Song[] = [];
  private index = 0;
  private readonly songCache = inject(SongCacheService);
  private currentSongSubject = new BehaviorSubject<Song | null>(null);
  currentSong$ = this.currentSongSubject.asObservable();

  constructor() {
    this.audio.addEventListener('ended', () => this.next());
  }

  loadPlaylist(songs: Song[]) {
    this.playlist = songs;
  }

  play(song?: Song) {
    if (song) {
      this.index = this.playlist.findIndex(s => s.song_id === song.song_id);
      this.songCache.getSongUrl(song.song_id, song.audio_url).subscribe({
        next: ({ url, fromCache}) => {
          this.audio.src = url;
          this.audio.load();
          this.audio.play();
          this.currentSongSubject.next(song);
          console.log(`Playing song ${song.song_id} from ${fromCache ? 'cache' : 'S3'}`);
        },
        error: (err) => {
          console.error('Failed to get song using cache service:', err);
          this.audio.src = song.audio_url;
          this.audio.load();
          this.audio.play();
          this.currentSongSubject.next(song);
        }
      });
    } else if (this.audio.paused) {
      this.audio.play();
    } else {
      this.audio.pause();
    }
  }

  pause() {
    this.audio.pause();
  }

  next() {
    if (this.playlist.length === 0) return;
    this.index = (this.index + 1) % this.playlist.length;
    this.play(this.playlist[this.index]);
  }

  previous() {
    if (this.playlist.length === 0) return;
    this.index = (this.index - 1 + this.playlist.length) % this.playlist.length;
    this.play(this.playlist[this.index]);
  }

  seekTo(percent: number) {
    if (this.audio.duration) {
      this.audio.currentTime = (percent / 100) * this.audio.duration;
    }
  }

  getProgressPercent(): number {
    if (!this.audio.duration) return 0;
    return (this.audio.currentTime / this.audio.duration) * 100;
  }

  onTimeUpdate(callback: (progress: number) => void) {
    this.audio.ontimeupdate = () => callback(this.getProgressPercent());
  }

  isPlaying(): boolean {
    return !this.audio.paused;
  }

  getCurrentTime(): number {
    return this.audio.currentTime || 0;
  }

  getDuration(): number {
    return this.audio.duration || 0;
  }

  destroy() {
    this.pause();
    this.audio = new Audio();
    this.playlist = [];
    this.index = 0;

    this.currentSongSubject = new BehaviorSubject<Song | null>(null);
    this.currentSong$ = this.currentSongSubject.asObservable();
  }
}
