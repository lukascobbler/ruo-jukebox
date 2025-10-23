import {Component, inject, OnInit} from '@angular/core';
import {ReactiveFormsModule} from "@angular/forms";
import {SongTableComponent} from "../song-table/song-table.component";
import {
  MatCell,
  MatCellDef,
  MatColumnDef,
  MatHeaderCell, MatHeaderCellDef,
  MatHeaderRow,
  MatHeaderRowDef,
  MatRow, MatRowDef, MatTable
} from '@angular/material/table';
import {MatIconButton} from '@angular/material/button';
import {AuthService} from '../../../services/auth/auth.service';
import { SubscriptionsService } from '../../../services/subscriptions/subscriptions.service';
import { ToastrService } from '../../../services/toastr/toastr.service';
import { firstValueFrom } from 'rxjs';
import {MatProgressSpinner} from '@angular/material/progress-spinner';
import {NgIf} from '@angular/common';
import {PlayerService} from '../../../services/player/player.service';

type Row = {
  topic: string;
  subscriptionName: string;
  type: 'artist' | 'genre';
};

@Component({
  selector: 'app-subscriptions',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatCell,
    MatCellDef,
    MatColumnDef,
    MatHeaderCell,
    MatHeaderRow,
    MatHeaderRowDef,
    MatIconButton,
    MatRow,
    MatRowDef,
    MatTable,
    MatHeaderCellDef,
    MatProgressSpinner,
    NgIf
  ],
  templateUrl: './subscriptions.component.html',
  styleUrl: './subscriptions.component.scss'
})
export class SubscriptionsComponent implements OnInit {
  auth = inject(AuthService);
  private subsService = inject(SubscriptionsService);
  private toast = inject(ToastrService);
  subscribedToDataSource: Row[] = [];
  busyTopics = new Set<string>();
  displayedColumns = ['subscriptionName', 'actions'];
  playerService = inject(PlayerService);
  loading = true;

  ngOnInit(): void {
    this.fetchMine();
  }

  private fetchMine(): void {
    this.subsService.listMine().subscribe({
      next: (payload) => {
        const rows: Row[] = [];

        for (const a of payload.artists || []) {
          rows.push({
            topic: a.id,
            subscriptionName: a.name,
            type: 'artist'
          });
        }

        for (const g of payload.genres || []) {
          rows.push({
            topic: g.id,
            subscriptionName: g.name,
            type: 'genre'
          });
        }

        rows.sort((x, y) =>
          x.type === y.type ? x.subscriptionName.localeCompare(y.subscriptionName)
                            : x.type.localeCompare(y.type)
        );

        this.subscribedToDataSource = rows;
        this.loading = false;
      },
      error: (err) => {
        const msg = this.extractError(err);
        this.toast.error('Failed to load subscriptions', msg);
      }
    });
  }

  async onUnsubscribe(row: Row) {
    if (this.busyTopics.has(row.topic)) return;
    this.busyTopics.add(row.topic);
    try {
      await firstValueFrom(this.subsService.delete(row.topic));
      this.subscribedToDataSource = this.subscribedToDataSource.filter(r => r.topic !== row.topic);
      this.toast.success('Unsubscribed', row.subscriptionName);
    } catch (err: any) {
      const msg = this.extractError(err);
      this.toast.error('Unsubscribe error', msg);
    } finally {
      this.busyTopics.delete(row.topic);
    }
  }

  private extractError(err: any): string {
    const msg = err?.error?.error || err?.error?.message || err?.message || 'Unexpected error. Please try again.';
    return typeof msg === 'string' ? msg : 'Unexpected error. Please try again.';
  }
}
