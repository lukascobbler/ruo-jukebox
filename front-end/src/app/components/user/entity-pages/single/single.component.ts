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
import {SongsService} from '../../../../services/singles/singles.service';
import {Single} from '../../../../models/Single';

@Component({
  selector: 'app-single',
  standalone: true,
  imports: [
    SongTableComponent,
    BoxMissingIconSmallComponent,
    MatProgressSpinner,
    NgIf
  ],
  templateUrl: './single.component.html',
  styleUrl: './single.component.scss'
})
export class SingleComponent implements OnInit {
  auth = inject(AuthService);
  route = inject(ActivatedRoute);
  singlesService = inject(SongsService);
  toast = inject(ToastrService)

  loading = true;
  single: Single | null = null;

  ngOnInit() {
    let singleId = this.route.snapshot.params['id'];

    this.singlesService.get(singleId).subscribe({
      next: value => {
        this.single = value;
        this.loading = false;
      },
      error: err => {
        this.toast.error("Error", "Error loading single: " + err);
        this.loading = false;
      }
    })
  }

  transformForSongsTable(): Song[] {
    return [this.single as Song];
  }
}
