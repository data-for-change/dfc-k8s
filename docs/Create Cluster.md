# Create Cluster

This document describes the procedure to create a new cluster.

## Prerequisites

* [eksctl](https://github.com/weaveworks/eksctl/releases/latest).
* [AWS CLI V2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
* [kubectl](https://kubernetes.io/releases/download/)

```
$ kubectl version --client --short 2>/dev/null
Client Version: v1.24.2
Kustomize Version: v4.5.4
$ aws --version
aws-cli/2.7.11 Python/3.9.11 Linux/5.13.0-51-generic exe/x86_64.ubuntu.20 prompt/off
$ eksctl version
0.103.0
```

## Create a new cluster

Create `kubernetes-admin` AWS IAM User (only if it doesn't already exist) 
with policies `AdministratorAccess`, `IAMUserChangePassword`

Get the access/secret keys for the `kubernetes-admin` AWS IAM user

Login to AWS with these credentials under profile `anyway-kubernetes-admin`

```
aws configure --profile anyway-kubernetes-admin
```

Set the profile in env var

```
export AWS_PROFILE=anyway-kubernetes-admin
```

Verify you are connected

```
$ aws sts get-caller-identity
{
    "UserId": "",
    "Account": "",
    "Arn": ""
}
```

Set the cluster name you want to create in an env var

```
CLUSTER_NAME=anyway-main
```

Create and edit the cluster configuration at `clusters/${CLUSTER_NAME}/eks-cluster.yaml`

Create the cluster

```
eksctl create cluster -f clusters/${CLUSTER_NAME}/eks-cluster.yaml
```

Set the cluster region in env var (according to what you defined in the cluster config)

```
export AWS_REGION=eu-central-1
```

Create a directory to store sensitive details for the cluster

```
sudo mkdir -p /etc/anyway/k8s/${CLUSTER_NAME} && sudo chown $USER -R /etc/anyway/k8s/${CLUSTER_NAME}
```

Create a kubeconfig file

```
export KUBECONFIG=/etc/anyway/k8s/${CLUSTER_NAME}/.kubeconfig
eksctl utils write-kubeconfig --region $AWS_REGION --cluster "${CLUSTER_NAME}" --kubeconfig "${KUBECONFIG}"
```

Verify connection to the cluster

```
kubectl get nodes
```

Store the .kubeconfig file in vault under `admin/k8s-${CLUSTER_NAME}-kubeconfig` in key `KUBECONFIG`

Create a .env file for the cluster:

```
echo "export CLUSTER_NAME=${CLUSTER_NAME}
export AWS_PROFILE=anyway-kubernetes-admin
export AWS_REGION=${AWS_REGION}
export KUBECONFIG=/etc/anyway/k8s/${CLUSTER_NAME}/.kubeconfig" > clusters/${CLUSTER_NAME}/.env
```

You should have a certificate in AWS certificate manager with wildcard domains to be served from this ingress.

The certificate arn should be defined in `clusters/${CLUSTER_NAME}/ingress-nginx-deploy-tls-termination.yaml` under `service.beta.kubernetes.io/aws-load-balancer-ssl-cert`

Deploy the ingress

```
kubectl apply -f clusters/${CLUSTER_NAME}/ingress-nginx-deploy-tls-termination.yaml
```

Verify that ingress was deployed

```
kubectl -n ingress-nginx get pods
```

Get the ingress hostname

```
kubectl -n ingress-nginx get service ingress-nginx-controller
```

Set a DNS CNAME from a relevant domain e.g. `k8s-${CLUSTER_NAME}-ingress.anyway.co.il` to this hostname

Write this domain in `clusters/${CLUSTER_NAME}/ingress-domain.txt`

To route individual domains via the ingress, use this custom DNS CNAME
