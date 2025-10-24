import { Injectable, inject } from '@angular/core';
import { from, Observable, of } from 'rxjs';
import { map, catchError, switchMap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class CacheService {
  private dbName = 'MusicCache';
  private dbVersion = 1;
  private storeName = 'songs';

  private openDB(): Observable<IDBDatabase> {
    return new Observable((observer) => {
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
      switchMap(
        (db) =>
          new Observable<void>((observer) => {
            const tx = db.transaction([this.storeName], 'readwrite');
            const store = tx.objectStore(this.storeName);
            const req = store.put(data, key);

            tx.oncomplete = () => {
              observer.next();
              observer.complete();
            };
            tx.onerror = () => observer.error(tx.error);
          })
      )
    );
  }

  get(key: string): Observable<Blob | null> {
    return this.openDB().pipe(
      switchMap(
        (db) =>
          new Observable<Blob | null>((observer) => {
            const tx = db.transaction([this.storeName], 'readonly');
            const store = tx.objectStore(this.storeName);
            const req = store.get(key);

            req.onsuccess = () => observer.next(req.result ?? null);
            req.onerror = () => observer.next(null);
          })
      )
    );
  }

  has(key: string): Observable<boolean> {
    return this.get(key).pipe(
      map(blob => blob !== null)
    );
  }

  delete(key: string): Observable<void> {
    return this.openDB().pipe(
      switchMap(
        (db) =>
          new Observable<void>((observer) => {
            const tx = db.transaction([this.storeName], 'readwrite');
            const store = tx.objectStore(this.storeName);
            const req = store.delete(key);

            tx.oncomplete = () => {
              observer.next();
              observer.complete();
            };
            tx.onerror = () => observer.error(tx.error);
          })
      )
    );
  }
}