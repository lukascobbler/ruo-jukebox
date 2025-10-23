import {Album} from './album/Album';
import {Song} from './Song';
import {Artist} from './Artist';

export interface SearchResult {
  singles: Song[];
  albums: Album[];
  artists: Artist[];
}
