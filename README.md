# Bookify Backend
Enigma | Hackathon | Bookify

Backend de l'application Bookify réalisé lors du Hackaton de l'école Enigma

L'application permet :
- L'enregistrement des utilisateurs
- L'authentification des utilisateurs
- Lire les informations du compte
- Recharger l'argent disponible sur le compte
- Récupérer la liste des livres
- Faire une recherche de livres par nom
- Faire une recherche de livres par ISBN
- Récupérer un livre
- Ajouter une offre de vente pour un livre
- Mettre à jour une offre de vente
- Supprimer une offre de vente
- Acheter un livre


## Architecture

![Architecture](https://lh3.googleusercontent.com/TCfaEixec-FnxWVRWNoVtxbfOaWFhJDQu3eHEZPeCBPkVgymjYYCHqjTrCWbFf1q9UJtJx4VSv8 "architecture")

L'architecture du projet est découpée comme suis :
- Une base de données Elasticsearch (version: 6.2.2) afin de stocker les données
- Une API en Python proposant un Swagger
- Un serveur HTTP Nginx servant de proxy entre internet et l'API
- Docker pour gérer le tout

Le projet possède 2 configurations, une pour le développement et une pour la production

### Développement

En configuration de développement :
- La base de données Elasticsearch est disponible sur le port 9200
- Le service d'envoi de email mailcatcher est disponible sur le port 1080
- L'API est disponible sur le port 80
- Le swagger est activé

### Production

En configuration de production :
- L'API est disponible sur le port 443
- Le swagger est désactivé

## Fonctions

En configuration de développement, l'ensemble des fonctions sont documentées sur un Swagger

![Swagger](https://lh3.googleusercontent.com/SePnVlbSJUVF2beLexUyLoZFzFdbFGJol2AFP0ALQVlSTMX2x8LuXNEeRVoRNPkeS9HVAMtyuz8 "Swagger")

### auth

L'espace de nom `auth` permet :
- Lire les informations du token d'authentification
- Générer un token d'authentification

### account

L'espace de nom `account` permet : 
- Lire les informations du compte de l'utilisateur authentifié
- Mettre à jour les informations du compte de l'utilisateur authentifié
- Déposer de l'argent sur le compte de l'utilisateur authentifié

### users

L'espace de nom `users` permet :
- Enregistrer un utilisateur
- Confirmer l'enregistrement d'un utilisateur

### books

L'espace de nom `books` permet :
- Récupérer la liste des livres
- Ajouter un livre
- Recherher un livre par nom
- Récupérer un livre à partir du numéro ISBN
- Récupérer un livre à partir de son identifiant unique

### offers

L'espace de nom `offers` permet :
- Ajouter une offre de vente
- Supprimer une offre de vente
- Modifier une offre de vente
- Acheter une offre de vente

# Installation

Cloner le projet :
```
git clone https://github.com/averdier/bookify_backend
```

## Génération des clés

Créer le dossier qui contiendra les clés
```
cd docker
mkdir keys
```

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 
Generating a 4096 bit RSA private key
................++
..................++
writing new private key to 'key.pem'
Enter PEM pass phrase:
Verifying - Enter PEM pass phrase:
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:FR
State or Province Name (full name) [Some-State]:France
Locality Name (eg, city) []:Lille
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Bitbot
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:
Email Address []:a.verdier@outlook.fr
```

```
openssl x509 -pubkey -noout -in cert.pem > auth_pubkey.pem
```

```
openssl rsa -in key.pem -out auth_privkey.pem 
Enter pass phrase for key.pem: 
writing RSA key
```

## Configuration du projet

### app.ini

Le fichier `/docker/config/app.ini` permet de paramétrer :
- Le nombre de processus de l'API
- Le point de montage de l'API

```
[uwsgi]
mount = /<mount_point>=wsgi.py
manage-script-name = true
master = true
processes = <processes>
socket = /sockets/bookify.socket
chmod-socket = 666
vacuum = true
die-on-term = true
```

### services.<prod|dev>.conf

Le fichier `/docker/config/services<prod|dev>.conf` permet de paramètrer :
- Le point de montage de l'API dans NGINX

```
server {
  listen 443 ssl;
  charset utf-8;
  location /<mount_point> {
    uwsgi_pass unix:/sockets/bookify.socket;
    uwsgi_param SCRIPT_NAME /<mount_point>;
    uwsgi_modifier1 30;
    include uwsgi_params;
  }
}
```

### docker-compose.yml

Le fichier `docker-compose.yml` permet de paramétrer :

`CERTS`: Le nom de domaine

`EMAIL`: L'adresse email de l'administrateur pour la génération des certificats let's encrypt

`ADMINS`: La liste des adresses email des administrateurs

`ELASTICSEARCH_HOST`: L'adresse de la base de données Elasticsearch

`ELASTICSEARCH_USER`: Nom d'utilisateur pour la connexion à la base de données Elasticsearch

`ELASTICSEARCH_SECRET`: Mot de passe pour la connexion à la base de données Elasticsearch

`PRIVATE_KEY`: Chemin de la clé privée pour la génération des tokens

`PUBLIC_KEY`: Chemin de la clé publique pour la génération des tokens

`MAIL_SERVER`: Adresse du serveur d'envoi de emails

`MAIL_PORT`: Port du serveur d'envoi de emails

`MAIL_USERNAME`: Nom d'utilisateur pour l'envoi de emails

`MAIL_DEFAULT_SENDER`: Adresse d'envoi de emails

`MAIL_USE_TLS`: Utilisation du TLS

`MAIL_USE_SSL`: Utilisation du SSL

`MAIL_DEBUG`: Affichage des logs d'envoi de emails

`LOG_PATH`: Chemin des fichiers de logs

```
version: "2"
services:
  nginx:
    build: ./nginx
    environment:
      - CERTS=bookify.ddns.net
      - EMAIL=a.verdier@outlook.fr
    networks:
      - services_network
    ports:
      - 80:80
      - 443:443
    volumes:
      - sockets:/sockets/
      - ./config/services.prod.conf:/etc/nginx/conf.d/bookify.ddns.net.conf
      - ./etc/ssl/dhparam:/etc/ssl/dhparam
      - ./etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - bookify_backend
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:6.2.2
    environment:
      - cluster.name=bookify-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m -XX:-AssumeMP"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    networks:
      - services_network
  bookify_backend:
    image: 'bookify_backend:dev'
    command: uwsgi app.ini
    environment:
      - ADMINS=a.verdier@outlook.fr
      - ELASTICSEARCH_HOST=elasticsearch
      - ELASTICSEARCH_USER=elastic
      - ELASTICSEARCH_SECRET=changeme
      - PRIVATE_KEY=/keys/auth_privkey.pem
      - PUBLIC_KEY=/keys/auth_pubkey.pem
      - MAIL_SERVER=smtp.googlemail.com
      - MAIL_PORT=465
      - MAIL_USERNAME=rasta.dev.02@gmail.com
      - MAIL_PASSWORD=
      - MAIL_DEFAULT_SENDER=rasta.dev.02@gmail.com
      - MAIL_USE_TLS=False
      - MAIL_USE_SSL=True
      - MAIL_DEBUG=True
      - LOG_PATH=/logs/bookify_backend.log
    volumes:
      - sockets:/sockets/
      - ./logs:/logs
      - ./keys:/keys/
      - ./config/app.ini:/bookify/app.ini
      - ./database:/database/
    networks:
      - services_network
volumes:
  sockets:
    driver: local
networks:
  services_network:
    driver: bridge
```

## Construire le projet

Construire l'image du projet
```
docker build -t bookify_backend:dev -f ./docker/Dockerfile .
```

## Lancement du projet

Le lancement du projet ce fait en 2 temps:
- Lancement de Elasticsearch
- Lancement du reste du projet

Lancement de Elasticsearch puis attendre 1 minute
```
docker-compose -f ./docker/docker-compose-prod.yml up -d elasticsearch
```

Lancement du reste du projet
```
docker-compose -f ./docker/docker-compose-prod.yml up -d
```