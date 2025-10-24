import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { env } from '../../../environments/environment';

export type CreateInteractionRequest = {
  songId: string | null;
  artist_ids: string[];
  genre_ids: string[];
  album_id?: string | null;
  value: number;
};

@Injectable({ providedIn: 'root' })
export class InteractionsService {
  private readonly http = inject(HttpClient);
  private readonly URL = `${env.API_URL}/interactions`;
  create(
    songId: string | null,
    artistIds: string[] = [],
    genreIds: string[] = [],
    albumId: string | null = null,
    value = 5
  ): Observable<void> {
    const body: CreateInteractionRequest = {
      songId,
      artist_ids: artistIds ?? [],
      genre_ids: genreIds ?? [],
      album_id: albumId ?? null,
      value
    };

    return this.http.post<void>(this.URL, body).pipe(
      catchError(err => {
        console.warn('Failed to create interaction:', err);
        return of(void 0);
      })
    );
  }
}
