# Docker

## Build

Build image
```
docker build -t bookify_backend:dev -f ./docker/Dockerfile .
```

## Run project

### Dev - HTTP
```
docker-compose -f ./docker/docker-compose-dev.yml up -d
```

### Prod - HTTPS
```
docker-compose -f ./docker/docker-compose-prod.yml up -d
```