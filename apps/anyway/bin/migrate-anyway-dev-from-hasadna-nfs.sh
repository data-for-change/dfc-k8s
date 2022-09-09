#!/usr/bin/env bash
# this script is used to migrate the anyway-dev storage from hasadna NFS to AWS pvc
# it is intended to run from hasadna's NFS server
# it's recommended to stop the relevant workloads which use the pvcs before running this script

bin/migrate_data_to_aws_pvc.sh /srv/default2/anyway-dev/airflow-db anyway-dev airflow-db 20Gi &&\
bin/migrate_data_to_aws_pvc.sh /srv/default2/anyway-dev/etl-data anyway-dev airflow-etl-data 200Gi &&\
bin/migrate_data_to_aws_pvc.sh /srv/default2/anyway-dev/airflow-home anyway-dev airflow-home-data 50Gi &&\
bin/migrate_data_to_aws_pvc.sh /srv/default2/anyway-dev/db anyway-dev db 200Gi
