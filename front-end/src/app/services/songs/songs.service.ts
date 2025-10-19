import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SongsService {
  private http = inject(HttpClient);
  private readonly API_BASE = 'https://api.jb.moma.rs/song';

  initUpload(payload: { name: string; artist_ids: string[]; genre_ids: string[]; filename: string; cover_filename?: string }): Observable<{ song_id: string; upload_url: string; cover_upload_url?: string }> {
    return this.http.post<{ song_id: string; upload_url: string; cover_upload_url?: string }>(`${this.API_BASE}/init-upload`, payload);
  }

  completeUpload(song_id: string): Observable<void> {
    return this.http.post<void>(`${this.API_BASE}/complete-upload`, { song_id });
  }

  deleteSong(song_id: string): Observable<void> {
    return this.http.delete<void>(`${this.API_BASE}/${song_id}`);
  }

  getSong(song_id: string): Observable<any> {
    return this.http.get<any>(`${this.API_BASE}/${song_id}`);
  }

  listSongs(): Observable<any[]> {
    return this.http.get<any[]>(`${this.API_BASE}`);
  }
}
