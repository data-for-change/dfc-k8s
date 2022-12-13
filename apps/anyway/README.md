# Anyway

## Architecture

https://docs.google.com/presentation/d/1bXkcCgsXUr1FQA7hCZdb5_m7IXIiP1UixuOHuV88sfs/edit?usp=sharing

![](image.png)

## Initial Deployment

* Create secrets
  * set env vars with the secret DB values
    * `POSTGRES_PASSWORD=`
    * `ANYWAY_PASSWORD=`
    * `DBRESTORE_AWS_ACCESS_KEY_ID=`
    * `DBRESTORE_AWS_SECRET_ACCESS_KEY=`
    * `DBDUMP_AWS_ACCESS_KEY_ID=`
    * `DBDUMP_AWS_SECRET_ACCESS_KEY=`
  * create the DB secrets:
    * `kubectl -n $NAMESPACE_NAME create secret generic anyway-db "--from-literal=DATABASE_URL=postgresql://anyway:${ANYWAY_PASSWORD}@db/anyway"`
    * `kubectl -n $NAMESPACE_NAME create secret generic db "--from-literal=DBRESTORE_SET_ANYWAY_PASSWORD=${ANYWAY_PASSWORD}" "--from-literal=POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" "--from-literal=DBRESTORE_AWS_ACCESS_KEY_ID=${DBRESTORE_AWS_ACCESS_KEY_ID}" "--from-literal=DBRESTORE_AWS_SECRET_ACCESS_KEY=${DBRESTORE_AWS_SECRET_ACCESS_KEY}"`
    * `kubectl -n $NAMESPACE_NAME create secret generic db-backup "--from-literal=DBDUMP_AWS_ACCESS_KEY_ID=${DBDUMP_AWS_ACCESS_KEY_ID}" "--from-literal=DBDUMP_AWS_SECRET_ACCESS_KEY=${DBDUMP_AWS_SECRET_ACCESS_KEY}" "--from-literal=DBDUMP_PASSWORD=${POSTGRES_PASSWORD}"`
  * Create the anyway secret (see the anyway production docker-compose for available values, or leave it empty just for basic testing)
    * `kubectl -n $NAMESPACE_NAME create secret generic anyway`

## Deployment

* For local deployment on Minikue - use Helm to deploy this chart with the values file `values-minikube.yaml`
* For production deployment - Use ArgoCD, see [/docs/argocd.md](/docs/argocd.md) for details.

## Enabling the Airflow server

Set the following values in `anyway` secret:

* `AIRFLOW_DB_POSTGRES_PASSWORD`: Generate a password (`python3 -c 'import secrets; print(secrets.token_hex(16))'`)
* `AIRFLOW_SQLALCHEMY_URL`: (replace AIRFLOW_DB_POSTGRES_PASSWORD with the password you generated) `postgresql://postgres:AIRFLOW_DB_POSTGRES_PASSWORD@airflow-db`
* `AIRFLOW_ADMIN_PASSWORD`: Generate a password (`python3 -c 'import secrets; print(secrets.token_hex(16))'`)

Enable airflow by setting `enableAirflow: true` in the relevant environment's values

Deploy

## Enable DB Redash read-only user

Start a shell on DB pod and run the following to start an sql session:

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
