import {Song} from '../Song';
import {Genre} from '../Genre';
import {Artist} from '../Artist';

export interface Album {
  content_id: string;
  name: string;
  picture?: Blob;
  artists: Artist[];
  released: boolean;
  cover_url: string;
  genres: Genre[];
  songs?: Song[]; // this field should be missing when an album is
                  // requested as an entity not on the individual album page
}
