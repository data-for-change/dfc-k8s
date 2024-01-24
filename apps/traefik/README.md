# Traefik

## Install

Set secrets in apps/traefik/secrets/traefik.env:

```
export ACME_EMAIL=
```

Create acme storage directory:

```
sudo mkdir -p /data/traefik/acme
```

## Deploy

```
apps/traefik/deploy.sh
```
