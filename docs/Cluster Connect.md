# Connect to the cluster

This is an advanced topic, you should not need to do this unless you are debugging a problem.

Required tools:

* [AWS CLI V2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
* [kubectl](https://kubernetes.io/releases/download/)

### Get admin credentials

This should be done only once and will be relevant for all clusters:

* Get the access/secret keys from vault `admin/aws-kubernetes-admin`
* Login to AWS with these credentials under profile `dfc-kubernetes-admin`
```
aws configure --profile dfc-kubernetes-admin
```

### Get the cluster admin kubeconfig

* Get the kubeconfig from vault `admin/k8s-main-kubeconfig`
* Save the contents of the KUBECONFIG key at `/etc/dfc/k8s/main/.kubeconfig`

### Connecting using kubectl

Clone the dfc-k8s repository and change directory to it

source the cluster .env file:

```
. clusters/main/.env
```

Verify connection to the cluster

```
kubectl get nodes
```

You can now run kubectl commands on the cluster
