import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {map, Observable, shareReplay} from 'rxjs';
import {GenreItem} from '../../models/GenreItem';
import {env} from '../../../environments/environment';

export interface GenreCreateRequest {
  name: string;
}

export interface GenreCreateResponse {
  id: string;
  name: string;
}

export interface GenreDetail {
  id: string;
  name: string;
}

@Injectable({providedIn: 'root'})
export class GenresService {

  private http = inject(HttpClient);

  create(name: string): Observable<GenreCreateResponse> {
    const body: GenreCreateRequest = {name: (name ?? '').trim()};
    return this.http.post<GenreCreateResponse>(`${env.API_URL}/genres`, body);
  }

  get(id: string): Observable<GenreDetail> {
    return this.http.get<GenreDetail>(`${env.API_URL}/genres/${encodeURIComponent(id)}`);
  }

  update(id: string, name: string): Observable<{ id: string; name: string }> {
    return this.http.patch<{ id: string; name: string }>(`${env.API_URL}/genres/${encodeURIComponent(id)}`,
      {name: (name ?? '').trim()}
    );
  }

  delete(id: string): Observable<{ id: string; deleted: { content_genres: number; genre: number } }> {
    return this.http.delete<{ id: string; deleted: { content_genres: number; genre: number } }>(
      `${env.API_URL}/genres/${encodeURIComponent(id)}`
    );
  }

  list(): Observable<GenreItem[]> {
    const url = `${env.API_URL}/genres`;
    return this.http.get<GenreItem[] | string>(url).pipe(
      map(res => Array.isArray(res) ? res : JSON.parse(res as string) as GenreItem[])
    );
  }

}
