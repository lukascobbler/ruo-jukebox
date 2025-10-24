import {Genre} from './Genre';
import {Artist} from './Artist';

export interface Song {
  content_id: string;
  pos?: number;
  name: string;
  album: string;
  album_id?: string;
  single_id?: string;
  duration: number;
  lyrics: string;
  genres: Genre[];
  artists: Artist[];
  cover_url?: string;
  audio_url: string;
}
