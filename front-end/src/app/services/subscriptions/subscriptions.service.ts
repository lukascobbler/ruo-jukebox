import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subscription } from '../../models/Subscription';
import { forkJoin, map, switchMap } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SubscriptionsService {
  private http = inject(HttpClient);
  private readonly API_URL = 'https://api.jb.moma.rs';

  private topicOf(id: string): 'ARTIST' | 'GENRE' {
    const p = id.split('~', 1)[0].toUpperCase();
    return p as 'ARTIST' | 'GENRE';
  }

  getMine() {
    type MineResp = {
      user_id: string;
      genres:  { id?: string; sk?: string }[];
      artists: { id?: string; sk?: string }[];
    };
    type GenresResp  = { items: { genre_id?: string; PK?: string; name?: string }[] };
    type ArtistsResp = { items: { artist_id?: string; PK?: string; name?: string; cover_key?: string }[] };

    const mine$    = this.http.get<MineResp>(`${this.API_URL}/subscriptions/mine`);
    const genres$  = this.http.get<GenresResp>(`${this.API_URL}/genres`);
    const artists$ = this.http.get<ArtistsResp>(`${this.API_URL}/artists`);

    // helper: from /subscriptions/mine entry -> prefixed id using either id or SK
    const toPrefixedFromMine = (entry: { id?: string; sk?: string }, topic: 'ARTIST'|'GENRE') => {
      if (entry?.id) return entry.id.includes('~') ? entry.id : `${topic}~${entry.id}`;
      const sk = entry?.sk ?? ''; // "SUB~TOPIC~uuid"
      const parts = sk.split('~', 3);
      const uuid = parts.length === 3 ? parts[2] : '';
      return `${topic}~${uuid}`;
    };

    return mine$.pipe(
      switchMap(mine =>
        forkJoin([genres$, artists$]).pipe(
          map(([gRes, aRes]) => {
            // build name lookups (keys are already prefixed)
            const genreName = new Map<string, string>();
            for (const g of gRes.items ?? []) {
              const gid = (g.genre_id || g.PK || '').toString();
              if (gid) genreName.set(gid, g.name ?? '');
            }

            const artistMeta = new Map<string, { name: string; cover_key?: string }>();
            for (const a of aRes.items ?? []) {
              const aid = (a.artist_id || a.PK || '').toString();
              if (aid) artistMeta.set(aid, { name: a.name ?? '', cover_key: a.cover_key });
            }

            const genres = (mine.genres ?? []).map(g => {
              const id = toPrefixedFromMine(g, 'GENRE');
              return { id, name: genreName.get(id) ?? '' };
            });

            const artists = (mine.artists ?? []).map(a => {
              const id = toPrefixedFromMine(a, 'ARTIST');
              const meta = artistMeta.get(id);
              return { id, name: meta?.name ?? '', pictureKey: meta?.cover_key };
            });

            const result: Subscription = { genres, artists };
            return result;
          })
        )
      )
    );
  }



  subscribe(id: string) { // "GENRE~{UUID}" or "ARTIST~{UUID}"
    return this.http.post(`${this.API_URL}/subscriptions`, { id });
  }
 
  unsubscribe(id: string) { // "GENRE~{UUID}" or "ARTIST~{UUID}"
    return this.http.request('DELETE', `${this.API_URL}/subscriptions/${this.topicOf(id)}`, { body: { id } });
  }
}
