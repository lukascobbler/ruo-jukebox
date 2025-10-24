import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import {env} from '../../../environments/environment';
import { InteractionsService } from '../interactions/interactions.service';
type RatingRecord = {
  user_id: string;
  song_id: string;
  rating: string;
};

@Injectable({ providedIn: 'root' })
export class RatingsService {
  private http = inject(HttpClient);
  private readonly API_URL = env.API_URL + '/rating';
  private readonly interaction = inject(InteractionsService)
  get(songId: string): Observable<number> {
    const url = `${this.API_URL}/${encodeURIComponent((songId ?? '').trim())}`;
    return this.http.get<RatingRecord[]>(url).pipe(
      map(arr => {
        const r = (arr && arr.length > 0) ? arr[0].rating : '0';
        const n = parseInt(r, 10);
        return Number.isFinite(n) ? n : 0;
      })
    );
  }

  set(songId: string, rating: number, artistIds: string[]  = [], genreIds:string[] = [], albumId: string | null = null): Observable<RatingRecord> {
    const body = { songId: (songId ?? '').trim(), rating: String(rating) };
    this.interaction
      .create(songId,artistIds,genreIds,albumId,rating*10)
      .subscribe();
    return this.http.put<RatingRecord>(this.API_URL, body);
  }


  delete(songId: string): Observable<void> {
    const body = { songId: (songId ?? '').trim() };
    return this.http.request<void>('DELETE', this.API_URL, { body });
  }
}
