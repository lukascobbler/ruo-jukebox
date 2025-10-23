import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subscription } from '../../models/Subscription';
import {env} from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class SubscriptionsService {
  private http = inject(HttpClient);

  create(targetId: string) {
    return this.http.post<{ targetId: string; created: boolean }>(`${env.API_URL}/subscriptions`, { targetId });
  }

  delete(targetId: string) {
    const enc = encodeURIComponent(targetId);
    return this.http.delete<{ targetId: string; deleted: boolean }>(`${env.API_URL}/subscriptions/${enc}`);
  }

  listMine() {
    return this.http.get<Subscription>(`${env.API_URL}/subscriptions/mine`);
  }
}
