import {Component, inject, OnInit} from '@angular/core';
import {SongTableComponent} from "../../song-table/song-table.component";
import {Album} from '../../../../models/Album';
import {
  BoxMissingIconSmallComponent
} from '../../../common/missing-icons/box/missing-icon-small/box-missing-icon-small.component';
import {AuthService} from '../../../../services/auth/auth.service';
import {Song} from '../../../../models/Song';
import {AlbumsService} from '../../../../services/albums/albums.service';
import {ActivatedRoute} from '@angular/router';
import {ToastrService} from '../../../../services/toastr/toastr.service';
import {MatProgressSpinner} from '@angular/material/progress-spinner';
import {NgIf} from '@angular/common';
import {PlayerService} from '../../../../services/player/player.service';

@Component({
  selector: 'app-musical-content',
  standalone: true,
  imports: [
    SongTableComponent,
    BoxMissingIconSmallComponent,
    MatProgressSpinner,
    NgIf
  ],
  templateUrl: './musical-content.component.html',
  styleUrl: './musical-content.component.scss'
})
export class MusicalContentComponent implements OnInit {
  auth = inject(AuthService);
  route = inject(ActivatedRoute);
  albumsService = inject(AlbumsService);
  toast = inject(ToastrService)
  playerService = inject(PlayerService);

  loading = true;
  album: Album | null = null;

  ngOnInit() {
    let albumId = this.route.snapshot.params['id'];

    this.albumsService.get(albumId).subscribe({
      next: value => {
        this.album = value;
        this.loading = false;
      },
      error: err => {
        this.toast.error("Error", "Error loading album: " + err);
        this.loading = false;
      }
    })
  }
}
