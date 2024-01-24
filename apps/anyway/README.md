# Anyway

## Architecture

https://docs.google.com/presentation/d/1bXkcCgsXUr1FQA7hCZdb5_m7IXIiP1UixuOHuV88sfs/edit?usp=sharing

![](image.png)

## Install

Set env vars for Vault access:

```
export VAULT_ADDR=
export VAULT_TOKEN=
```

Set secret values:

```
bin/render_env_template.py apps/anyway/secrets/anyway.env.template > apps/anyway/secrets/anyway.env
bin/render_env_template.py apps/anyway/secrets/anyway-db.env.template > apps/anyway/secrets/anyway-db.env
bin/render_env_template.py apps/anyway/secrets/db.env.template > apps/anyway/secrets/db.env
bin/render_env_template.py apps/anyway/secrets/airflow-db.env.template > apps/anyway/secrets/airflow-db.env
bin/render_env_template.py apps/anyway/secrets/airflow-scheduler.env.template > apps/anyway/secrets/airflow-scheduler.env
bin/render_env_template.py apps/anyway/secrets/airflow-webserver.env.template > apps/anyway/secrets/airflow-webserver.env
vault kv get -format=json kv/projects/anyway/prod/k8s-secret-anyway | jq -r '.data.data["GOOGLE_APPLICATION_CREDENTIALS_KEY.json"]' > apps/anyway/secrets/GOOGLE_APPLICATION_CREDENTIALS_KEY.json
```

Run:

```
( cd apps/anyway && docker compose up -d )
```

### TODO: db-backup-cronjob
### TODO: ingresses
### TODO: airflow execute via kubectl exec - modify to execute in docker compose
### TODO: check anyway nginx proxy and configurations - for new docker compose hostnames

## Enable DB Redash read-only user

Start a shell on DB container and run the following to start an sql session:

```
su postgres
psql anyway
```

Run the following to create the readonly user (replace **** with real password):

```
CREATE ROLE readonly;
GRANT CONNECT ON DATABASE anyway TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
CREATE USER redash WITH PASSWORD '*****';
GRANT readonly TO redash;
```

See [this document](https://github.com/hasadna/anyway/blob/dev/docs/REDASH.md) for how to grant permissions for tables to this user.

## Restore from backup

Production DB has a daily backup which can be used to populate a new environment's DB

Following steps are for restoring to dev environment:

* stop the dev DB by scaling the db deployment down to 0 replicas
* clear the DB data directory (TBD: how to do this?)
* Edit the environment values (e.g. `values-anyway-dev.yaml`) and set `dbRestoreFileName` to the current day's date.
* Deploy the anyway chart - this will cause DB to be recreated from the backup
* The restore can take a long time..
