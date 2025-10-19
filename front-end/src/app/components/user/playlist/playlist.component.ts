import {Component, inject} from '@angular/core';
import {SongTableComponent} from "../song-table/song-table.component";
import {Playlist} from '../../../models/Playlist';
import {AuthService} from '../../../services/auth/auth.service';

@Component({
  selector: 'app-playlist',
  standalone: true,
    imports: [
        SongTableComponent
    ],
  templateUrl: './playlist.component.html',
  styleUrl: './playlist.component.scss'
})
export class PlaylistComponent {
  auth = inject(AuthService);

  playlist: Playlist = {'id': '', name: 'Awesome playlist'};
}
