# FrontEnd

## Development server
```shell
ng serve
```

## Deployment
```shell
ng build --configuration production  # build
aws s3 sync dist/front-end/browser/ s3://jukebox-frontend/ --delete  # upload
aws cloudfront create-invalidation --distribution-id E1IC7OO1GXB8I4 --paths "/*"  # invalidate cache
```
