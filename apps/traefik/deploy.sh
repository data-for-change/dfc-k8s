#!/usr/bin/env bash

. apps/traefik/secrets/traefik.env
envsubst < apps/traefik/traefik.yaml.template > apps/traefik/traefik.yaml
bin/compose traefik up -d
