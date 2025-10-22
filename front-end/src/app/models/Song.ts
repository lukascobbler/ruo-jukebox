import {GenreItem} from './GenreItem';
import {Artist} from './Artist';

export interface Song {
  song_id: string;
  no?: number;
  name: string;
  album: string;
  albumId: string;
  artistId: string;
  duration: number;
  lyrics: string;
  genres: GenreItem[];
  artists: Artist[];
  cover_url: string;
  audio_url: string;
}
