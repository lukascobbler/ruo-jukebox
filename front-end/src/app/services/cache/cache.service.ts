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
              db.close();
              observer.next();
              observer.complete();
            };
            tx.onerror = () => {
              const err = (tx.error ?? req.error) as any;
              db.close();
              observer.error(err);
            };

            req.onerror = () => {};
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

            tx.oncomplete = () => {
              db.close();
              observer.complete();
            };
            tx.onerror = () => {
              const err = (tx.error ?? req.error) as any;
              db.close();
              observer.error(err);
            };

            req.onsuccess = () => observer.next(req.result ?? null);
          })
      )
    );
  }

  has(key: string): Observable<boolean> {
    return this.get(key).pipe(
      map((blob) => blob !== null),
      catchError(() => of(false))
    );
  }

  delete(key: string): Observable<void> {
    return this.openDB().pipe(
      switchMap(
        (db) =>
          new Observable<void>((observer) => {
            const tx = db.transaction([this.storeName], 'readwrite');
            const store = tx.objectStore(this.storeName);
            store.delete(key);

            tx.oncomplete = () => {
              db.close();
              observer.next();
              observer.complete();
            };
            tx.onerror = () => {
              const err = tx.error as any;
              db.close();
              observer.error(err);
            };
          })
      )
    );
  }
}
