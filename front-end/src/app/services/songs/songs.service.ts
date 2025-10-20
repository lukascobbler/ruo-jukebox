import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface UploadInitPayload {
  name: string;
  artists: string[];
  genres: string[];
  filename: string;
  cover_filename?: string;
}

export interface UploadInitResponse {
  song_id: string;
  upload_url: string;
  cover_upload_url?: string;
}

@Injectable({ providedIn: 'root' })
export class SongsService {
  private readonly http = inject(HttpClient);
  private readonly API_BASE = 'https://api.jb.moma.rs/song';

  initUpload(payload: UploadInitPayload): Observable<UploadInitResponse> {
    return this.http.post<UploadInitResponse>(`${this.API_BASE}/init-upload`, payload);
  }

  completeUpload(song_id: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.API_BASE}/complete-upload`, { song_id });
  }

  deleteSong(song_id: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.API_BASE}/${song_id}`);
  }

  getSong(song_id: string): Observable<any> {
    return this.http.get<any>(`${this.API_BASE}/${song_id}`);
  }

  listSongs(): Observable<any[]> {
    return this.http.get<any[]>(`${this.API_BASE}`);
  }

  updateSong(
    song_id: string,
    payload: {
      name?: string;
      artist_ids?: string[];
      genre_ids?: string[];
      cover_filename?: string;
      audio_filename?: string;
    }
  ): Observable<{ message: string; cover_upload_url?: string; audio_upload_url?: string }> {
    return this.http.patch<{ message: string; cover_upload_url?: string; audio_upload_url?: string }>(
      `${this.API_BASE}/${song_id}`,
      { song_id, ...payload }
    );
  }
}
