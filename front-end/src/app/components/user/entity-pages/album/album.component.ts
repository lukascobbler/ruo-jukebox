import {Component, inject} from '@angular/core';
import {SongTableComponent} from "../../song-table/song-table.component";
import {Album} from '../../../../models/album/Album';
import {
  BoxMissingIconSmallComponent
} from '../../../common/missing-icons/box/missing-icon-small/box-missing-icon-small.component';
import {AuthService} from '../../../../services/auth/auth.service';
import {Song} from '../../../../models/Song';

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

  album: Album = { id: '1', name: 'Awesome album', artists: [{
      name: "Artist 1", artist_id: "1", cover_key: null, cover_url: null, biography: "", genres: [], singles: [], albums: []
    }], genres: [{genre_id: '1', name: 'jazz'}, {genre_id: '2', name: 'country'}, {genre_id: '3', name: 'rock'}], released: false };

  getArtists() {
    return this.album.artists.map(a => a.name).join(" ")
  }
}
