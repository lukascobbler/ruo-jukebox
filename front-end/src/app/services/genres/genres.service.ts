import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from '../auth/auth.service';

export interface GenreCreateRequest { name: string; }
export interface GenreCreateResponse { id: string; name: string; }
export interface GenreListItem { id: string; name: string; isSubscribed: boolean | null; }
export interface GenreDetail { id: string; name: string; }

@Injectable({ providedIn: 'root' })
export class GenresService {
  private readonly API_URL = 'https://api.jb.moma.rs';

  private http = inject(HttpClient);
  private auth = inject(AuthService);

  private authHeaders(): HttpHeaders {
    const token = this.auth.getToken();
    return new HttpHeaders(token ? { Authorization: `Bearer ${token}` } : {});
  }

  create(name: string): Observable<GenreCreateResponse> {
    const body: GenreCreateRequest = { name: (name ?? '').trim() };
    return this.http.post<GenreCreateResponse>(`${this.API_URL}/genres`, body, {
      headers: this.authHeaders(),
    });
  }

  list(): Observable<GenreListItem[]> {
    return this.http.get<GenreListItem[]>(`${this.API_URL}/genres`, {
      headers: this.authHeaders(),
    });
  }

  get(id: string): Observable<GenreDetail> {
    return this.http.get<GenreDetail>(`${this.API_URL}/genres/${encodeURIComponent(id)}`, {
      headers: this.authHeaders(),
    });
  }

  update(id: string, name: string): Observable<{ id: string; name: string }> {
    return this.http.patch<{ id: string; name: string }>(
      `${this.API_URL}/genres/${encodeURIComponent(id)}`,
      { name: (name ?? '').trim() },
      { headers: this.authHeaders() }
    );
  }

  delete(id: string): Observable<{ id: string; deleted: { content_genres: number; genre: number } }> {
    return this.http.delete<{ id: string; deleted: { content_genres: number; genre: number } }>(
      `${this.API_URL}/genres/${encodeURIComponent(id)}`,
      { headers: this.authHeaders() }
    );
  }
}
