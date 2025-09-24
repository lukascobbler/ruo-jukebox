import {Genre} from './Genre';

export interface Song {
  id: string;
  no?: number;
  title: string;
  album: string;
  albumId: string;
  artist: string;
  artistId: string;
  duration: number;
  lyrics: string;
  genres: Genre[];
}
