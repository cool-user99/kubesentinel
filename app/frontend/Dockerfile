# --- Étape 1 : build — compile l'application Angular (Node n'est utile qu'ici)
FROM node:22.23.4-alpine AS builder
WORKDIR /build
# Copier d'abord les manifestes : la couche npm ci reste en cache tant qu'ils ne changent pas
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# --- Étape 2 : runtime — nginx non-root (UID 101) qui sert les fichiers statiques
FROM nginxinc/nginx-unprivileged:1.30.6-alpine3.24
# Correctifs Alpine publiés après la construction de l'image de base (root requis, USER 101 plus bas)
USER 0
RUN apk upgrade --no-cache
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /build/dist/frontend/browser /usr/share/nginx/html
USER 101
EXPOSE 8080
