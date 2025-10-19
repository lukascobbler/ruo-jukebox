import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { BehaviorSubject, Observable } from 'rxjs';
import {Role} from '../../models/Role';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly API_URL = 'https://api.jb.moma.rs';
  private readonly TOKEN_KEY = 'access_token';
  private readonly ID_TOKEN_KEY = 'id_token';

  private roleSubject = new BehaviorSubject<Role | null>(null);
  role$ = this.roleSubject.asObservable();

  constructor(private http: HttpClient) {
    this.updateRoleFromStorage();
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.API_URL}/auth/login`, {
      username: email,
      password,
    }).pipe(
      tap((res: any) => {
        localStorage.setItem(this.TOKEN_KEY, res.access_token);
        if (res.id_token) localStorage.setItem(this.ID_TOKEN_KEY, res.id_token);
        this.updateRoleFromStorage();
      })
    );
  }

  register(data: any): Observable<any> {
    return this.http.post(`${this.API_URL}/auth/register`, {
      username: data.username,
      email: data.email,
      password: data.password,
      first_name: data.name,
      last_name: data.surname,
      birthday: data.dateOfBirth,
    });
  }

  logout(): void {
    const token = this.getToken();
    if (token) {
      this.http.post(`${this.API_URL}/auth/logout`, { access_token: token }).subscribe({
        next: () => this.clear(),
        error: () => this.clear(),
      });
    } else {
      this.clear();
    }
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  getIdToken(): string | null {
    return localStorage.getItem(this.ID_TOKEN_KEY);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  clear(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.ID_TOKEN_KEY);
    this.roleSubject.next(null);
  }

  private decodeToken(token: string | null): any | null {
    if (!token) return null;
    try {
      const payload = token.split('.')[1];
      const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
      return JSON.parse(decoded);
    } catch {
      return null;
    }
  }

  private updateRoleFromStorage(): void {
    const idToken = this.getIdToken();
    const decoded = this.decodeToken(idToken);
    let newRole: Role = 'User';

    if (decoded && decoded['cognito:groups']?.includes('Admin')) {
      newRole = 'Admin';
    }

    this.roleSubject.next(this.isLoggedIn() ? newRole : null);
  }

  getRole(): Observable<Role | null> {
    return this.role$;
  }

  getCurrentRole(): Role | null {
    return this.roleSubject.value;
  }

  isAdmin(): boolean {
    return this.roleSubject.value === 'Admin';
  }
}
