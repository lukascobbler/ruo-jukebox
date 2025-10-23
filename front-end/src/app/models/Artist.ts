import {Genre} from './Genre';
import {Song} from './Song';
import {Album} from './album/Album';

export interface Artist {
  artist_id: string;
  name: string;
  cover_key: string | null;
  cover_url: string | null;
  biography: string;
  genres: Genre[];
  isSubscribed?: boolean; // this field should be missing when the admin requests an artist
  singles: Song[];
  albums: Album[];
}
