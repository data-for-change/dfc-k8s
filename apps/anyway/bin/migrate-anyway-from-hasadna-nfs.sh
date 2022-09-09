#!/usr/bin/env bash
# this script is used to migrate the anyway storage from hasadna NFS to AWS pvc
# it is intended to run from hasadna's NFS server
# it's recommended to stop the relevant workloads which use the pvcs before running this script

bin/migrate_data_to_aws_pvc.sh /srv/default2/anyway/airflow-db anyway airflow-db 20Gi &&\
bin/migrate_data_to_aws_pvc.sh /srv/default2/anyway/etl-data anyway airflow-etl-data 200Gi &&\
bin/migrate_data_to_aws_pvc.sh /srv/default2/anyway/airflow-home anyway airflow-home-data 50Gi &&\
bin/migrate_data_to_aws_pvc.sh /srv/default2/anyway/db anyway db 200Gi
