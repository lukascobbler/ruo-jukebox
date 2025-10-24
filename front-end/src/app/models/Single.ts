import {Artist} from './Artist';
import {Song} from './Song';
import {Genre} from './Genre';

export interface Single extends Song {
  content_id: string;
  name: string;
  song_id: string;
  audio_url: string;
  cover_url?: string;
  artists: Artist[];
  genres: Genre[];
  duration: number;
}
