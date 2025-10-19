import {Component} from '@angular/core';
import {SongTableComponent} from "../../song-table/song-table.component";
import {Album} from '../../../../models/Album';
import {
  BoxMissingIconSmallComponent
} from '../../../common/missing-icons/box/missing-icon-small/box-missing-icon-small.component';

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
  album: Album = { id: '1', name: 'Awesome album', artist: 'Awesome artist', artistId: '1', genres: [{id: '1', name: 'jazz'}, {id: '2', name: 'country'}, {id: '3', name: 'rock'}] };
}
