import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {map, Observable} from 'rxjs';
import {GenreItem} from '../../models/GenreItem';
import {env} from '../../../environments/environment';
import {Genre} from '../../models/Genre';


@Injectable({providedIn: 'root'})
export class GenresService {

  private http = inject(HttpClient);

  get(id: string): Observable<Genre> {
    return this.http.get<Genre>(`${env.API_URL}/genres/${encodeURIComponent(id)}`);
  }
  list(): Observable<GenreItem[]> {
    return this.http
      .get<GenreItem[]>(`${env.API_URL}/genres`)
      .pipe(shareReplay(1));
  }
}
