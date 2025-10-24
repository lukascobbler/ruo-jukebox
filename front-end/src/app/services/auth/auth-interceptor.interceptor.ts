import {HttpInterceptorFn} from '@angular/common/http';
import {inject} from '@angular/core';
import {Router} from '@angular/router';
import {catchError} from 'rxjs/operators';
import {throwError} from 'rxjs';
import {AuthService} from './auth.service';

function isPresignedS3(urlStr: string): boolean {
  // Detect S3/CloudFront presigned URLs by domain + X-Amz-* signature params
  try {
    const u = new URL(urlStr, window.location.origin);
    const host = u.hostname;
    const qp = u.searchParams;
    const isAwsHost = host.includes('amazonaws.com') || host.includes('cloudfront.net');
    const hasSig = qp.has('X-Amz-Algorithm') || qp.has('X-Amz-Signature');
    return isAwsHost && hasSig;
  } catch {
    return false; // relative URLs won't be presigned S3
  }
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (isPresignedS3(req.url)) {
    return next(req);
  }
  const token = auth.getIdToken();
  const isAuthEndpoint = req.url.includes('/auth/login') || req.url.includes('/auth/register');
  const authReq = !isAuthEndpoint && token ? req.clone({setHeaders: {Authorization: `Bearer ${token}`},}) : req;
  return next(authReq).pipe(
    catchError((error) => {
      if (error.status === 401) {
        auth.logout();
        router.navigate(['/login']);
      }
      return throwError(() => error);
    })
  );
};
