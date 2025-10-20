import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subscription } from '../../models/Subscription';

@Injectable({ providedIn: 'root' })
export class SubscriptionsService {
  private http = inject(HttpClient);
  private readonly API_URL = 'https://api.jb.moma.rs';

  create(topic: string) {
    return this.http.post<{ topic: string; created: boolean }>(`${this.API_URL}/subscriptions`, { topic });
  }

  delete(topic: string) {
    const enc = encodeURIComponent(topic);
    return this.http.delete<{ topic: string; deleted: boolean }>(`${this.API_URL}/subscriptions/${enc}`);
  }

  listMine() {
    return this.http.get<Subscription>(`${this.API_URL}/subscriptions/mine`);
  }
}
