import {Song} from './Song';

export interface Playlist {
  id: string;
  name: string;
  songs?: Song[]; // this field should be missing when the user requests a list of his playlists,
                  // and it should contain songs on the individual playlist page
}
