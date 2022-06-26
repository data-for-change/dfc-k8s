# Velero

[Velero](https://velero.io/) is used for backups of persistent storage and Kubernetes data.

## Install

* Download [latest velero release binary](https://github.com/vmware-tanzu/velero/releases/latest)
* Connect to relevant cluster
* Create S3 bucket:
  * name: `data-for-change-k8s-CLUSTER_NAME-velero-backups`
  * region: same as cluster
  * object ownership: ACLs disabled
  * Block all public access
  * Bucket versioning: disable
  * Encryption: disabled
* Create AWS IAM user:
  * name: `data-for-change-k8s-CLUSTER_NAME-velero-backups`
  * access type: programatic
  * no permissions
  * save the credentials in vault under `k8s/CLUSTER_NAME/aws-velero-iam-user`
    * AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
* Add inline policy to the user:
  * name: `data-for-change-k8s-CLUSTER_NAME-velero-backups`
  * content (replace CLUSTER_NAME with the cluster name):
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeVolumes",
                "ec2:DescribeSnapshots",
                "ec2:CreateTags",
                "ec2:CreateVolume",
                "ec2:CreateSnapshot",
                "ec2:DeleteSnapshot"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:PutObject",
                "s3:AbortMultipartUpload",
                "s3:ListMultipartUploadParts"
            ],
            "Resource": [
                "arn:aws:s3:::data-for-change-k8s-CLUSTER_NAME-velero-backups/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::data-for-change-k8s-CLUSTER_NAME-velero-backups"
            ]
        }
    ]
}
```
* Create a local file named `credentials-velero` with the access key / secret for this user:
```
[default]
aws_access_key_id=<AWS_ACCESS_KEY_ID>
aws_secret_access_key=<AWS_SECRET_ACCESS_KEY>
```
* Set env vars:
  * `CLUSTER_NAME=`
  * `REGION=`
* Install velero:
```
velero install \
    --provider aws \
    --plugins velero/velero-plugin-for-aws:v1.4.0 \
    --bucket data-for-change-k8s-${CLUSTER_NAME}-velero-backups \
    --backup-location-config region=$REGION \
    --snapshot-location-config region=$REGION \
    --secret-file ./credentials-velero
```
