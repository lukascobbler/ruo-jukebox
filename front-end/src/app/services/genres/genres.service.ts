import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable, shareReplay} from 'rxjs';
import {env} from '../../../environments/environment';
import {Genre} from '../../models/Genre';


@Injectable({providedIn: 'root'})
export class GenresService {

  private http = inject(HttpClient);

  get(id: string): Observable<Genre> {
    return this.http.get<Genre>(`${env.API_URL}/genres/${encodeURIComponent(id)}`);
  }

  list(): Observable<Genre[]> {
    return this.http
      .get<Genre[]>(`${env.API_URL}/genres`)
      .pipe(shareReplay(1));
  }
}
