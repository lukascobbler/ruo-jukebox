import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, switchMap, catchError, tap } from 'rxjs/operators';
import { CacheService } from '../cache/cache.service';

@Injectable({ providedIn: 'root' })
export class SongCacheService {
  private readonly cache = inject(CacheService);
  private readonly http = inject(HttpClient);

  cacheSong(songId: string, audioUrl: string): Observable<void> {
    console.log('Caching song:', songId);

    if (!songId || !songId.startsWith('SONG~')) {
      throw new Error('Invalid songId format');
    }

    return this.http.get(audioUrl, { responseType: 'blob' }).pipe(
      switchMap((blob) => this.cache.set(songId, blob)),
      tap(() => console.log('Song cached successfully:', songId)),
      catchError((error) => {
        console.error('Failed to cache song:', error);
        throw error;
      })
    );
  }

  getSongUrl(songId: string, fallbackUrl: string): Observable<{ url: string; fromCache: boolean }> {
    return this.cache.get(songId).pipe(
      switchMap((cachedBlob) => {
        if (cachedBlob) {
          const url = URL.createObjectURL(cachedBlob);
          return of({ url, fromCache: true });
        } else {
          return of({ url: fallbackUrl, fromCache: false });
        }
      }),
      catchError(() => of({ url: fallbackUrl, fromCache: false }))
    );
  }

  isCached(songId: string): Observable<boolean> {
    return this.cache.has(songId).pipe(
      catchError(() => of(false))
    );
  }

  removeFromCache(songId: string): Observable<void> {
    return this.cache.delete(songId);
  }

  downloadCachedSong(songId: string, songName: string): Observable<void> {
    return this.cache.get(songId).pipe(
      switchMap((blob) => {
        if (!blob) {
          throw new Error('Song not found in cache');
        }
        this.triggerDownload(blob, songName);
        return of(void 0);
      }),
      catchError((error) => {
        console.error('Failed to download cached song:', error);
        throw error;
      })
    );
  }

  private triggerDownload(blob: Blob, fileName: string): void {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${this.cleanFileName(fileName)}.mp3`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  private cleanFileName(name: string): string {
    return name
      .replace(/[^a-zA-Z0-9\s\-_]/g, '')
      .replace(/\s+/g, '_')
      .substring(0, 100);
  }
}
