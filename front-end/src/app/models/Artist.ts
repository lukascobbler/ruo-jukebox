import {GenreItem} from './GenreItem';

export interface Artist {
  id: string;
  name: string;
  pictureKey: string | null;
  pictureUrl: string | null;
  biography: string;
  genres: GenreItem[];
  isSubscribed?: boolean; // this field should be missing when the admin requests an artist
}