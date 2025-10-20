import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {Album} from '../../models/album/Album';

export interface AlbumUpdateRequest {
  name?: string;
  artistId?: string;
  genreIds?: string[];
}

export interface UploadInitPayload {
  name: string;
  artists: string[];
  genres: string[];
  cover_filename?: string;
}

export interface UploadInitResponse {
  album_id: string;
  upload_url: string;
  cover_upload_url?: string;
}

@Injectable({providedIn: 'root'})
export class AlbumsService {
  private readonly API_URL = 'https://api.jb.moma.rs';
  private readonly http = inject(HttpClient);

  list(): Observable<Album[]> {
    return this.http.get<Album[]>(`${this.API_URL}/albums`);
  }

  release(id: string): Observable<void> {
    return this.http.post<void>(`${this.API_URL}/albums/${encodeURIComponent(id)}`, {});
  }

  initUpload(payload: UploadInitPayload): Observable<UploadInitResponse> {
    return this.http.post<UploadInitResponse>(`${this.API_URL}/init-upload`, payload);
  }

  completeUpload(album_id: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.API_URL}/complete-upload`, { album_id });
  }

  get(id: string): Observable<Album> {
    return this.http.get<Album>(`${this.API_URL}/albums/${encodeURIComponent(id)}`);
  }

  update(id: string, body: AlbumUpdateRequest): Observable<void> {
    return this.http.patch<void>(
      `${this.API_URL}/albums/${encodeURIComponent(id)}`,
      body
    );
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(
      `${this.API_URL}/albums/${encodeURIComponent(id)}`
    );
  }
}
