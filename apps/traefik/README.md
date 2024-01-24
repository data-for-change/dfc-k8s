# Traefik

## Install

Set acme email env var:

```
export ACME_EMAIL=
```

Generate template:

```
envsubst < apps/traefik/traefik.yaml.template > apps/traefik/traefik.yaml
```

Create acme storage directory:

```
sudo mkdir -p /data/traefik/acme
```