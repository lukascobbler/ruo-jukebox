import {GenreItem} from './GenreItem';

export interface Artist {
  artist_id: string;
  name: string;
  cover_key: string | null;
  cover_url: string | null;
  biography: string;
  genres: GenreItem[];
  isSubscribed?: boolean; // this field should be missing when the admin requests an artist
}
