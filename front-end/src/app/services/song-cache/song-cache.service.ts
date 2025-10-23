// song-cache.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, switchMap, catchError, tap } from 'rxjs/operators';
import { CacheService } from '../cache/cache.service';

@Injectable({
  providedIn: 'root'
})
export class SongCacheService {
  private readonly cache = inject(CacheService);
  private readonly http = inject(HttpClient);


  cacheSong(songId: string, audioUrl: string): Observable<void> {
    return this.http.get(audioUrl, { responseType: 'blob' }).pipe(
      switchMap(blob => this.cache.set(songId, blob)),
      catchError(error => {
        console.error('Failed to cache song:', error);
        throw error;
      })
    );
  }

  getSong(songId: string, fallbackUrl: string): Observable<{ blob: Blob; fromCache: boolean }> {
    const cacheKey = songId;
    
    return this.cache.get(cacheKey).pipe(
      switchMap(cachedBlob => {
        if (cachedBlob) {
          console.log('Returning song from cache:', songId);
          return [{ blob: cachedBlob, fromCache: true }];
        } else {
          console.log('No cached song, fetching song from S3:', songId);
          return this.http.get(fallbackUrl, { responseType: 'blob' }).pipe(
            map(blob => ({ blob, fromCache: false }))
          );
        }
      }),
      catchError(error => {
        console.error('Error getting song:', error);
        // If everything fails, try to get from fallback URL
        return this.http.get(fallbackUrl, { responseType: 'blob' }).pipe(
          map(blob => ({ blob, fromCache: false }))
        );
      })
    );
  }

  isCached(songId: string): Observable<boolean> {
    return this.cache.has(songId);
  }

  removeFromCache(songId: string): Observable<void> {
    return this.cache.delete(songId);
  }

  getCachedSongUrl(songId: string): Observable<string | null> {
    return this.cache.get(songId).pipe(
      map(blob => blob ? URL.createObjectURL(blob) : null)
    );
  }

  downloadSong(songId: string, songName: string, audioUrl: string): Observable<void> {
    return this.http.get(audioUrl, { responseType: 'blob' }).pipe(
      tap(blob => {
        this.triggerDownload(blob, songName);
      }),
      map(() => void 0),
      catchError(error => {
        console.error('Failed to download song:', error);
        throw error;
      })
    );
  }

  downloadCachedSong(songId: string, songName: string): Observable<void> {
    return this.cache.get(songId).pipe(
      tap(blob => {
        if (blob) {
          console.log('Downloading cached song:', songId);
          this.triggerDownload(blob, songName);
        } else {
          throw new Error('Song not found in cache');
        }
      }),
      map(() => void 0),
      catchError(error => {
        console.error('Failed to download cached song:', error);
        throw error;
      })
    );
  }

  smartDownload(songId: string, songName: string, audioUrl: string): Observable<void> {
    return this.isCached(songId).pipe(
      switchMap(isCached => {
        if (isCached) {
          return this.downloadCachedSong(songId, songName);
        } else {
          return this.downloadSong(songId, songName, audioUrl);
        }
      })
    );
  }

  private triggerDownload(blob: Blob, fileName: string): void {
    const cleanFileName = this.cleanFileName(fileName);
    
    const url = window.URL.createObjectURL(blob);
    
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${cleanFileName}.mp3`;
    anchor.style.display = 'none';
    
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    
    window.URL.revokeObjectURL(url);
  }

  private cleanFileName(name: string): string {
    return name
      .replace(/[^a-zA-Z0-9\s\-_]/g, '')
      .replace(/\s+/g, '_')
      .substring(0, 100);
  }
}