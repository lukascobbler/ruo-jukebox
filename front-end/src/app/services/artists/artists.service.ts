import {inject, Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Observable, map} from 'rxjs';

export interface CreateArtistRequest {
  name: string;
  biography: string;
  genres: string[];     // array of GENRE~uuid
  pictureKey?: string;  // usually omit; picture is attatched later via upload flow
}
export interface CreateArtistResponse {
  id: string;
  name: string;
  biography: string;
  pictureKey?: string | null;
  genres: { id: string; name: string }[];
}
export interface InitUploadResp { uploadUrl: string; key: string; expiresIn: number; }
export interface CompleteUploadResp { id: string; pictureKey: string; saved: boolean; }

@Injectable({providedIn: 'root'})
export class ArtistsService {
  private readonly API_URL = 'https://api.jb.moma.rs';
  private http = inject(HttpClient);

  create(req: CreateArtistRequest): Observable<CreateArtistResponse> {
    return this.http
      .post<CreateArtistResponse | string>(`${this.API_URL}/artists`, req)
      .pipe(map(r => (typeof r === 'string' ? JSON.parse(r) : r)));
  }

  initPictureUpload(artistId: string, contentType: string): Observable<InitUploadResp> {
    return this.http
      .post<InitUploadResp | string>(`${this.API_URL}/artists/${encodeURIComponent(artistId)}/picture/init_upload`, {contentType})
      .pipe(map(r => (typeof r === 'string' ? JSON.parse(r) : r)));
  }

  completePictureUpload(artistId: string, key: string): Observable<CompleteUploadResp> {
    return this.http
      .post<CompleteUploadResp | string>(`${this.API_URL}/artists/${encodeURIComponent(artistId)}/picture/complete_upload`, {key})
      .pipe(map(r => (typeof r === 'string' ? JSON.parse(r) : r)));
  }

  // PUT the file to the presigned URL (no auth headers needed)
  uploadToS3(uploadUrl: string, file: File, contentType: string): Observable<void> {
    const headers = new HttpHeaders({'Content-Type': contentType});
    return this.http.put(uploadUrl, file, {headers, responseType: 'text'}).pipe(map(() => void 0));
  }
}
