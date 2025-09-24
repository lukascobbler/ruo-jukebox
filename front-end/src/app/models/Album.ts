import {Song} from './Song';

export interface Album {
  id: string;
  name: string;
  picture?: Blob;
  artist: string;
  artistId: string;
  songs?: Song[]; // this field should be missing when an album is
                  // requested as an entity not on the individual album page
}
