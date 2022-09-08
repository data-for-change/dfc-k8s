# Backups

Backups are handled using [Velero](https://velero.io/) deployed on the cluster. It handles the
following backups:

* Kubernetes etcd data is stored in S3 bucket `dfc-k8s-main-velero-backups`
* Persistent volumes are stored using AWS EBS snapshots

Backup schedules are defined in [/apps/velero-backups](/apps/velero-backups), currently
we have a daily backup with retention of 720 hours.
