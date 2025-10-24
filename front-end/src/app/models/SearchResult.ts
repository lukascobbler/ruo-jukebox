import {Album} from './Album';
import {Song} from './Song';
import {Artist} from './Artist';
import {Single} from './Single';

export interface SearchResult {
  songs: Song[];
  albums: Album[];
  artists: Artist[];
}
