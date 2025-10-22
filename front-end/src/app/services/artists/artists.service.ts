import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { Artist } from '../../models/Artist';
import {env} from '../../../environments/environment';

export interface CreateArtistRequest {
  name: string;
  biography: string;
  genres: string[]; // array of GENRE~uuid
  pictureKey?: string; // usually omit; picture is attatched later via upload flow
}
export interface CreateArtistResponse {
  id: string;
  name: string;
  biography: string;
  pictureKey?: string | null;
  genres: { id: string; name: string }[];
}
export interface InitUploadResp {
  uploadUrl: string;
  key: string;
  expiresIn: number;
}
export interface CompleteUploadResp {
  id: string;
  pictureKey: string;
  saved: boolean;
}

@Injectable({ providedIn: 'root' })
export class ArtistsService {
  private http = inject(HttpClient);

  create(req: CreateArtistRequest): Observable<CreateArtistResponse> {
    return this.http
      .post<CreateArtistResponse | string>(`${env.API_URL}/artists`, req)
      .pipe(map((r) => (typeof r === 'string' ? JSON.parse(r) : r)));
  }

  initPictureUpload(
    artistId: string,
    contentType: string
  ): Observable<InitUploadResp> {
    return this.http
      .post<InitUploadResp | string>(
        `${env.API_URL}/artists/${encodeURIComponent(
          artistId
        )}/picture/init_upload`,
        { contentType }
      )
      .pipe(map((r) => (typeof r === 'string' ? JSON.parse(r) : r)));
  }

  completePictureUpload(
    artistId: string,
    key: string
  ): Observable<CompleteUploadResp> {
    return this.http
      .post<CompleteUploadResp | string>(
        `${env.API_URL}/artists/${encodeURIComponent(
          artistId
        )}/picture/complete_upload`,
        { key }
      )
      .pipe(map((r) => (typeof r === 'string' ? JSON.parse(r) : r)));
  }

  // PUT the file to the presigned URL (no auth headers needed)
  uploadToS3(
    uploadUrl: string,
    file: File,
    contentType: string
  ): Observable<void> {
    const headers = new HttpHeaders({ 'Content-Type': contentType });
    return this.http
      .put(uploadUrl, file, { headers, responseType: 'text' })
      .pipe(map(() => void 0));
  }

  getAll(): Observable<Artist[]> {
    return this.http.get<Artist[] | string>(`${env.API_URL}/artists`).pipe(
      map((res) =>
        Array.isArray(res) ? res : (JSON.parse(res as string) as Artist[])
      ),
      map((items) =>
        items.map((a) => ({
          id: a.id,
          name: a.name,
          biography: a.biography,
          genres: a.genres,
          pictureKey: null,
          pictureUrl: null,
          isSubscribed: false,
        }))
      )
    );
  }
  getByGenre(genreId: string) {
    return this.http
      .get<Artist[] | string>(
        `${env.API_URL}/artists/by-genre/${encodeURIComponent(genreId)}`
      )
      .pipe(
        map((res) =>
          Array.isArray(res) ? res : (JSON.parse(res as string) as Artist[])
        )
      );
  }

  searchByName(q: string) {
    const url = `${env.API_URL}/artists/search?q=${encodeURIComponent(q)}`;
    return this.http.get<Artist[] | string>(url).pipe(
      map(res => Array.isArray(res) ? res : JSON.parse(res as string) as Artist[])
    );
  }


}
