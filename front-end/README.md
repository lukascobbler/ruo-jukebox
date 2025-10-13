# FrontEnd

## Development server
```shell
ng serve
```

## Deployment
```shell
ng build --configuration production  # build
aws s3 sync dist/front-end/browser/ s3://jukebox-front/ --delete  # upload
aws cloudfront create-invalidation --distribution-id EM6G5WF99MQNC --paths "/*"  # invalidate cache
```
