import {Song} from '../Song';
import {GenreItem} from '../GenreItem';

export interface Album {
  id: string;
  name: string;
  picture?: Blob;
  artist: string;
  artistId: string;
  released: boolean;
  genres: GenreItem[];
  songs?: Song[]; // this field should be missing when an album is
                  // requested as an entity not on the individual album page
}
