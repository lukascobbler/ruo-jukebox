import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly API_URL = 'https://your-api-gateway-url'; // replace with your API Gateway base URL
  private readonly TOKEN_KEY = 'access_token';

  constructor(private http: HttpClient) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.API_URL}/auth/login`, {
      username: email, // Cognito uses username — if you log in with email, backend maps it
      password,
    }).pipe(
      tap((res: any) => {
        localStorage.setItem(this.TOKEN_KEY, res.access_token);
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

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  clear(): void {
    localStorage.removeItem(this.TOKEN_KEY);
  }
}
