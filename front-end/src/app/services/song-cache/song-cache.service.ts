import {Injectable, inject} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable, of} from 'rxjs';
import {map, switchMap, catchError, tap} from 'rxjs/operators';
import {CacheService} from '../cache/cache.service';
import {AuthService} from '../auth/auth.service';
import {env} from '../../../environments/environment';
import { InteractionsService } from '../interactions/interactions.service';

type CreateInteractionRequest = {
  songId: string;
  artist_ids: string[];
  genre_ids: string[];
  album_id?: string | null;
};

@Injectable({providedIn: 'root'})
export class SongCacheService {
  private readonly cache = inject(CacheService);
  private readonly http = inject(HttpClient);
  private readonly INTERACTIONS_URL = `${env.API_URL}/interactions`;
  private readonly auth = inject(AuthService);
  private readonly interaction = inject(InteractionsService)

  cacheSong(songId: string, audioUrl: string): Observable<void> {
    console.log(songId)
      const key = `SONG~${(songId ?? '').trim()}`;
  if (!key || key === 'SONG~') {
    throw new Error('[cacheSong] invalid songId');
  }
    return this.http.get(audioUrl, {responseType: 'blob'}).pipe(
      switchMap((blob) => this.cache.set(songId, blob)),
      catchError((error) => {
        console.error('Failed to cache song:', error);
        throw error;
      })
    );
  }

  // Blob-based getter
  getSong(
    songId: string,
    fallbackUrl: string
  ): Observable<{ blob: Blob; fromCache: boolean }> {
    return this.cache.get(songId).pipe(
      switchMap((cachedBlob) => {
        if (cachedBlob) {
          return [{blob: cachedBlob, fromCache: true}];
        }
        return this.http
          .get(fallbackUrl, {responseType: 'blob'})
          .pipe(map((blob) => ({blob, fromCache: false})));
      }),
      catchError(() =>
        this.http
          .get(fallbackUrl, {responseType: 'blob'})
          .pipe(map((blob) => ({blob, fromCache: false})))
      )
    );
  }

  // URL resolver
  getSongUrl(
    songId: string,
    fallbackUrl: string,
    artistIds = ['hardcodeArtist'],
    genreIds = ['hardcodeGenre'],
    albumId: string | null = null
  ): Observable<{ url: string; fromCache: boolean }> {
    return this.cache.get(songId).pipe(
      tap(() => {
        if (this.auth.isAdmin()) {
          this.interaction
          .create(songId,artistIds,genreIds,albumId,1)
          .subscribe();
        }
      }),
      map((blob) => {
        if (blob) {
          const url = URL.createObjectURL(blob);
          return {url, fromCache: true as const};
        }
        return {url: fallbackUrl, fromCache: false as const};
      }),
      catchError(() => of({url: fallbackUrl, fromCache: false as const}))
    );
  }

  isCached(songId: string) {
    return this.cache.has(songId);
  }

  removeFromCache(songId: string) {
    return this.cache.delete(songId);
  }

  getCachedSongUrl(songId: string): Observable<string | null> {
    return this.cache
      .get(songId)
      .pipe(map((blob) => (blob ? URL.createObjectURL(blob) : null)));
  }

  downloadSong(
    songId: string,
    songName: string,
    audioUrl: string
  ): Observable<void> {
    return this.http.get(audioUrl, {responseType: 'blob'}).pipe(
      tap((blob) => this.triggerDownload(blob, songName)),
      map(() => void 0),
      catchError((error) => {
        console.error('Failed to download song:', error);
        throw error;
      })
    );
  }

  downloadCachedSong(songId: string, songName: string): Observable<void> {
    return this.cache.get(songId).pipe(
      tap((blob) => {
        if (!blob) throw new Error('Song not found in cache');
        this.triggerDownload(blob, songName);
      }),
      map(() => void 0),
      catchError((error) => {
        console.error('Failed to download cached song:', error);
        throw error;
      })
    );
  }

  smartDownload(
    songId: string,
    songName: string,
    audioUrl: string
  ): Observable<void> {
    return this.isCached(songId).pipe(
      switchMap((isCached) =>
        isCached
          ? this.downloadCachedSong(songId, songName)
          : this.downloadSong(songId, songName, audioUrl)
      )
    );
  }

  private triggerDownload(blob: Blob, fileName: string): void {
    const clean = this.cleanFileName(fileName);
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `${clean}.mp3`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  private cleanFileName(name: string): string {
    return name
      .replace(/[^a-zA-Z0-9\s\-_]/g, '')
      .replace(/\s+/g, '_')
      .substring(0, 100);
  }
}
