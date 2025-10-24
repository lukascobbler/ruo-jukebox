import {inject, Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Observable, map} from 'rxjs';
import {Artist} from '../../models/Artist';
import {env} from '../../../environments/environment';

export interface CreateArtistRequest {
  name: string;
  biography?: string;
  genres?: string[];
  cover?: boolean;
}

export interface CreateArtistResponse {
  artist_id: string;
  cover_url?: string;
}

export interface CompleteUploadResp {
  artist_id: string;
  name: string;
  biography?: string;
  cover_key?: string | null;
  genres: { genre_id: string; name: string }[];
}

@Injectable({providedIn: 'root'})
export class ArtistsService {
  private http = inject(HttpClient);

  create(req: CreateArtistRequest): Observable<CreateArtistResponse> {
    return this.http
      .post<CreateArtistResponse | string>(`${env.API_URL}/artists/init-upload`, req)
      .pipe(map(r => (typeof r === 'string' ? JSON.parse(r) : r)));
  }

  completeUpload(body: {
    artist_id: string;
    name: string;
    biography?: string;
    genres?: string[];
  }): Observable<CompleteUploadResp> {
    return this.http
      .post<CompleteUploadResp | string>(`${env.API_URL}/artists/complete-upload`, body)
      .pipe(map(r => (typeof r === 'string' ? JSON.parse(r) : r)));
  }

  getAll(): Observable<Artist[]> {
    return this.http.get<Artist[] | string>(`${env.API_URL}/artists`).pipe(
      map(res => (Array.isArray(res) ? res : (JSON.parse(res as string) as Artist[])))
    );
  }

  get(artistId: string): Observable<Artist> {
    return this.http.get<Artist>(`${env.API_URL}/artists/${artistId}`)
  }

  deleteArtist(artist_id: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${env.API_URL}/artists/${artist_id}`);
  }
}
