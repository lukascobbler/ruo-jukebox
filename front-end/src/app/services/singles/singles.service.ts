import {Injectable, inject} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {env} from '../../../environments/environment';

export interface UploadInitPayload {
  cover: boolean;
}

export interface UploadInitResponse {
  song_id: string;
  single_id: string;
  audio_url: string;
  cover_url?: string;
}

export interface UploadCompletePayload {
  name: string;
  song_id: string;
  single_id: string;
  artists: string[];
  genres: string[];
}

export interface UpdateSongPayload {
  name?: string;
  artist_ids?: string[];
  genre_ids?: string[];
  cover_filename?: string;
  audio_filename?: string;
}

export interface UpdateSongResponse {
  song_id: string;
  upload_url: string;
  cover_upload_url?: string;
}

@Injectable({providedIn: 'root'})
export class SongsService {
  private readonly http = inject(HttpClient);

  initUpload(payload: UploadInitPayload): Observable<UploadInitResponse> {
    return this.http.post<UploadInitResponse>(`${env.API_URL}/single/init-upload`, payload);
  }

  completeUpload(payload: UploadCompletePayload): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${env.API_URL}/single/complete-upload`, payload);
  }

  deleteSinge(song_id: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${env.API_URL}/single/${song_id}`);
  }

  listSingles(): Observable<any[]> {
    return this.http.get<any[]>(`${env.API_URL}/single`);
  }

  updateSingle(song_id: string, payload: UpdateSongPayload): Observable<{ message: string; cover_upload_url?: string; audio_upload_url?: string }> {
    return this.http.patch<{ message: string; cover_upload_url?: string; audio_upload_url?: string }>(
      `${env.API_URL}/single/${song_id}`,
      {song_id, ...payload}
    );
  }
}
