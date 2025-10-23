import { Injectable, inject } from '@angular/core';
import { from, Observable } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class CacheService {
  private dbName = 'MusicCache';
  private dbVersion = 1;
  private storeName = 'songs';

  private openDB(): Observable<IDBDatabase> {
    return new Observable(observer => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => observer.error(request.error);
      request.onsuccess = () => {
        observer.next(request.result);
        observer.complete();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName);
        }
      };
    });
  }

  set(key: string, data: Blob): Observable<void> {
    return this.openDB().pipe(
      switchMap(db => {
        return new Observable<void>(observer => {
          const transaction = db.transaction([this.storeName], 'readwrite');
          const store = transaction.objectStore(this.storeName);
          const request = store.put(data, key);

          request.onerror = () => {
            observer.error(request.error);
            db.close();
          };
          request.onsuccess = () => {
            observer.next();
            observer.complete();
            db.close();
          };
        });
      })
    );
  }

  get(key: string): Observable<Blob | null> {
    return this.openDB().pipe(
      switchMap(db => {
        return new Observable<Blob | null>(observer => {
          const transaction = db.transaction([this.storeName], 'readonly');
          const store = transaction.objectStore(this.storeName);
          const request = store.get(key);

          request.onerror = () => {
            observer.error(request.error);
            db.close();
          };
          request.onsuccess = () => {
            observer.next(request.result || null);
            observer.complete();
            db.close();
          };
        });
      })
    );
  }

  has(key: string): Observable<boolean> {
    return this.get(key).pipe(
      map(blob => blob !== null),
      catchError(() => [false])
    );
  }

  delete(key: string): Observable<void> {
    return this.openDB().pipe(
      switchMap(db => {
        return new Observable<void>(observer => {
          const transaction = db.transaction([this.storeName], 'readwrite');
          const store = transaction.objectStore(this.storeName);
          const request = store.delete(key);

          request.onerror = () => {
            observer.error(request.error);
            db.close();
          };
          request.onsuccess = () => {
            observer.next();
            observer.complete();
            db.close();
          };
        });
      })
    );
  }
}