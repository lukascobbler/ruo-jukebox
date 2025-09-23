import { Component } from '@angular/core';
import {
    BoxMissingIconSmallComponent
} from "../../common/missing-icons/box/missing-icon-small/box-missing-icon-small.component";
import {SongTableComponent} from "../song-table/song-table.component";
import {Playlist} from '../../../models/Playlist';

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
  playlist: Playlist = {'id': '', name: 'Awesome playlist'};
}
