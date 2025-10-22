import {inject, Injectable} from '@angular/core';
import {env} from '../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {SearchResult} from '../../models/SearchResult';

@Injectable({
  providedIn: 'root'
})
export class SearchService {

  private http = inject(HttpClient);

  search(query: string): Observable<SearchResult> {
    return this.http.get<SearchResult>(`${env.API_URL}/search/${query}`);
  }
}
