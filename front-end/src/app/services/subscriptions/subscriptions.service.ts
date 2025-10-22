import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subscription } from '../../models/Subscription';
import {env} from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class SubscriptionsService {
  private http = inject(HttpClient);

  create(topic: string) {
    return this.http.post<{ topic: string; created: boolean }>(`${env.API_URL}/subscriptions`, { topic });
  }

  delete(topic: string) {
    const enc = encodeURIComponent(topic);
    return this.http.delete<{ topic: string; deleted: boolean }>(`${env.API_URL}/subscriptions/${enc}`);
  }

  listMine() {
    return this.http.get<Subscription>(`${env.API_URL}/subscriptions/mine`);
  }
}
