import {Artist} from './Artist';
import {Song} from './Song';
import {Genre} from './Genre';

export interface Single extends Song {
  name: string;
  content_id: string;
  audio_url: string;
  cover_url?: string;
  artists: Artist[];
  genres: Genre[];
  duration: number;
  song_id: string;
}
