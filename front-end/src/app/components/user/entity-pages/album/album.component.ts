import {Component, inject} from '@angular/core';
import {SongTableComponent} from "../../song-table/song-table.component";
import {Album} from '../../../../models/album/Album';
import {
  BoxMissingIconSmallComponent
} from '../../../common/missing-icons/box/missing-icon-small/box-missing-icon-small.component';
import {AuthService} from '../../../../services/auth/auth.service';

@Component({
  selector: 'app-album',
  standalone: true,
  imports: [
    SongTableComponent,
    BoxMissingIconSmallComponent
  ],
  templateUrl: './album.component.html',
  styleUrl: './album.component.scss'
})
export class AlbumComponent {
  auth = inject(AuthService);

  album: Album = { id: '1', name: 'Awesome album', artist: 'Awesome artist', artistId: '1', genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false };
}
