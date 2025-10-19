import {GenreItem} from './GenreItem';

export interface Artist {
  id: string;
  name: string;
  picture?: Blob;
  biography: string;
  genres: GenreItem[];
  isSubscribed?: boolean; // this field should be missing when the admin requests an artist
}
