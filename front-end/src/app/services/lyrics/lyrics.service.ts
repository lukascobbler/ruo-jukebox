import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {env} from '../../../environments/environment';

export interface Lyrics {
  lyrics: string;
}

@Injectable({
  providedIn: 'root'
})
export class LyricsService {

  private http = inject(HttpClient);

  get(song_id: string): Observable<Lyrics> {
    return this.http.get<Lyrics>(`${env.API_URL}/lyrics/${encodeURIComponent(song_id)}`);
  }
}
