import {Artist} from './Artist';

export interface SingleItem {
  content_id: string;
  name: string;
  song_id: string;
  audio_url: string;
  cover_url?: string;
  artists: Artist[];
  genres: { name: string }[];
  duration: number;
}
