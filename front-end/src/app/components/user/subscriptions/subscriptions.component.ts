import { Component } from '@angular/core';
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

@Component({
  selector: 'app-subscriptions',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    SongTableComponent,
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
    MatHeaderCellDef
  ],
  templateUrl: './subscriptions.component.html',
  styleUrl: './subscriptions.component.scss'
})
export class SubscriptionsComponent {
  displayedColumns = ['subscriptionName', 'actions'];
  subscribedToDataSource = [
    {subscriptionName: "Awesome artist"},
    {subscriptionName: "Awesome genre"},
    {subscriptionName: "Awesome artist"},
    {subscriptionName: "Awesome genre"},
    {subscriptionName: "Awesome artist"},
    {subscriptionName: "Awesome genre"},
    {subscriptionName: "Awesome artist"},
    {subscriptionName: "Awesome genre"},
    {subscriptionName: "Awesome artist"},
  ];
}
