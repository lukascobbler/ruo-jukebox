import {Song} from '../Song';
import {GenreItem} from '../GenreItem';
import {Artist} from '../Artist';

export interface Album {
  id: string;
  name: string;
  picture?: Blob;
  artists: Artist[];
  released: boolean;
  genres: GenreItem[];
  songs?: Song[]; // this field should be missing when an album is
                  // requested as an entity not on the individual album page
}
