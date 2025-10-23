import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {Album} from '../../models/album/Album';
import {env} from '../../../environments/environment';
import {Artist} from '../../models/Artist';
import {Genre} from '../../models/Genre';
import {Song} from '../../models/Song';

export interface OfflineAlbumRequest {
  name: string;
  coverFile: File | null | undefined;
  selectedArtists: string[];
  selectedGenres: string[];
}

export interface OfflineSongRequest {
  name: string;
  audioFile: File;
  selectedArtists: string[];
  selectedGenres: string[];
  song_id?: string;
  artists: Artist[];
  genres: Genre[];
}

export interface UploadInitPayload {
  cover: boolean;
  numberOfSongs: number;
}

export interface UploadInitResponse {
  album_id: string;
  cover_url?: string;
  songs: {
    song_id: string; audio_url: string
  }[];
}

export interface UploadCompletePayload {
  name: string;
  album_id: string;
  artists: string[];
  genres: string[];
  songs: {
    song_id: string; name: string; genres: string[]; artists: string[];
  }[];
}

@Injectable({providedIn: 'root'})
export class AlbumsService {
  private readonly http = inject(HttpClient);

  initUpload(payload: UploadInitPayload): Observable<UploadInitResponse> {
    return this.http.post<UploadInitResponse>(`${env.API_URL}/album/init-upload`, payload);
  }

  completeUpload(payload: UploadCompletePayload): Observable<void> {
    return this.http.post<void>(`${env.API_URL}/album/complete-upload`, payload);
  }

  list(): Observable<Album[]> {
    return this.http.get<Album[]>(`${env.API_URL}/album`);
  }

  getSongs(album_id: string): Observable<Song> {
    return this.http.get<Song>(`${env.API_URL}/album/${album_id}`);
  }
}
