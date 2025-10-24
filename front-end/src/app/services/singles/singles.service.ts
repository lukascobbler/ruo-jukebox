import {env} from '../../../environments/environment';
import {Injectable, inject} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Single} from '../../models/Single';
import {Observable} from 'rxjs';

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

export interface CompleteUploadResponse {
  single_id: string;
  name: string;
  artists: { artist_id: string; name: string }[];
  genres: { genre_id: string; name: string }[];
  cover_key?: string;
}


@Injectable({providedIn: 'root'})
export class SongsService {
  private readonly http = inject(HttpClient);

  initUpload(payload: UploadInitPayload): Observable<UploadInitResponse> {
    return this.http.post<UploadInitResponse>(`${env.API_URL}/single/init-upload`, payload);
  }

  completeUpload(payload: UploadCompletePayload): Observable<CompleteUploadResponse> {
    return this.http.post<CompleteUploadResponse>(`${env.API_URL}/single/complete-upload`, payload);
  }

  deleteSingle(content_id: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${env.API_URL}/single/${content_id}`);
  }

  listSingles(): Observable<Single[]> {
    return this.http.get<Single[]>(`${env.API_URL}/single`);
  }

  get(content_id: string): Observable<Single> {
    return this.http.get<Single>(`${env.API_URL}/single/${content_id}`);
  }

  updateSingle(content_id: string, payload: Partial<UploadCompletePayload>): Observable<{ message: string; cover_upload_url?: string; audio_upload_url?: string }> {
    return this.http.patch<{ message: string; cover_upload_url?: string; audio_upload_url?: string }>(
      `${env.API_URL}/single/${content_id}`,
      {content_id, ...payload}
    );
  }
}
