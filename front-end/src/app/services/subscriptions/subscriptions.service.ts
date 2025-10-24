import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subscription } from '../../models/Subscription';
import {env} from '../../../environments/environment';
import { InteractionsService } from '../interactions/interactions.service';

@Injectable({ providedIn: 'root' })
export class SubscriptionsService {
  private http = inject(HttpClient);
  private readonly interaction = inject(InteractionsService)
  create(targetId: string,  songId: string | null, artistIds: string[]  = [], genreIds:string[] = [], albumId: string | null = null) {
    this.interaction
      .create(songId,artistIds,genreIds,albumId,50)
      .subscribe();
    return this.http.post<{ targetId: string; created: boolean }>(`${env.API_URL}/subscriptions`, { targetId });
  }

  delete(targetId: string,  songId: string | null, artistIds: string[]  = [], genreIds:string[] = [], albumId: string | null = null ) {
    const enc = encodeURIComponent(targetId);
    this.interaction
      .create(songId,artistIds,genreIds,albumId,-50)
      .subscribe();
    return this.http.delete<{ targetId: string; deleted: boolean }>(`${env.API_URL}/subscriptions/${enc}`);
  }

  listMine() {
    return this.http.get<Subscription>(`${env.API_URL}/subscriptions/mine`);
  }
}
