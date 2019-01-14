docker build -t bookify_backend:dev -f ./docker/Dockerfile .

docker-compose -f ./docker/docker-compose-dev.yml up -d