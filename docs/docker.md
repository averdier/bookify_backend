# Docker

## Build

Build image
```
docker build -t bookify_backend:dev -f ./docker/Dockerfile .
```

## Run image

### Http

Run backend with http server
> You should have auth_privkey.pem and auth_pubkey.pem in run directory

#### Windows
> Create c:/docker and put keys inside
```
docker run -d --name bookify_backend_dev -p 5555:5555 -v c:/docker/auth_privkey.pem:/bookify/auth_privkey.pem -v c:/docker/auth_pubkey.pem:/bookify/auth_pubkey.pem bookify_backend:dev uwsgi --http :5555 --wsgi-file wsgi.py
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