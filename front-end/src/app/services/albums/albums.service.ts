import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {Album} from '../../models/album/Album';

export interface AlbumCreateRequest {
  name: string;
  artistId: string;
  genreIds: string[];
}

export interface AlbumUpdateRequest {
  name?: string;
  artistId?: string;
  genreIds?: string[];
}

export interface InitCoverUploadResponse {
  uploadUrl: string;
  fileKey: string;
}

export interface CompleteCoverUploadRequest {
  fileKey: string;
  albumId: string;
}

@Injectable({providedIn: 'root'})
export class AlbumsService {
  private readonly API_URL = 'https://api.jb.moma.rs';
  private readonly http = inject(HttpClient);

  create(request: AlbumCreateRequest): Observable<Album> {
    return this.http.post<Album>(`${this.API_URL}/albums`, request);
  }

  list(): Observable<Album[]> {
    return this.http.get<Album[]>(`${this.API_URL}/albums`);
  }

  initCoverUpload(): Observable<InitCoverUploadResponse> {
    return this.http.post<InitCoverUploadResponse>(
      `${this.API_URL}/albums/init-cover-upload`,
      {}
    );
  }

  completeCoverUpload(req: CompleteCoverUploadRequest): Observable<{ success: boolean }> {
    return this.http.post<{ success: boolean }>(
      `${this.API_URL}/albums/complete-cover`,
      req
    );
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
