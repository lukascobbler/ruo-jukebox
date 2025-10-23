import {Album} from './album/Album';
import {Artist} from './Artist';

export interface Genre {
  genre_id: string;
  name: string;
  albums?: Album[];
  artists?: Artist[];
  isSubscribed?: boolean; // this field should be missing when the admin requests a genre
}
