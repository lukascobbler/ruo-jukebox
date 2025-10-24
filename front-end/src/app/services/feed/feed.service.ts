import {inject, Injectable} from '@angular/core';
import {env} from '../../../environments/environment';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {SearchResult} from '../../models/SearchResult';

@Injectable({
  providedIn: 'root'
})
export class FeedService {

  private http = inject(HttpClient);

  get(): Observable<SearchResult> {
    return this.http.get<SearchResult>(`${env.API_URL}/feed`);
  }
}
