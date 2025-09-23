import {Genre} from './Genre';

export interface Artist {
  id: string;
  name: string;
  picture?: Blob;
  biography: string;
  genres: Genre[];
  isSubscribed?: boolean; // this field should be missing when the admin requests an artist
}
