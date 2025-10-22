import {Album} from './album/Album';
import {Artist} from './Artist';

export interface Genre {
  id: string;
  name: string;
  albums: Album[];
  artists: Artist[];
}
