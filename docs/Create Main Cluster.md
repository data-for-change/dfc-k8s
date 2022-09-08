# Create Main Cluster

This document describes the procedure used to create the main dfc cluster

## Prerequisites

* [eksctl](https://github.com/weaveworks/eksctl/releases/latest).
* [AWS CLI V2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
* [kubectl](https://kubernetes.io/releases/download/)

```
$ kubectl version --client --short 2>/dev/null
Client Version: v1.24.2
Kustomize Version: v4.5.4
$ aws --version
aws-cli/2.7.21 Python/3.9.11 Linux/5.15.0-46-generic exe/x86_64.ubuntu.20 prompt/off
$ eksctl version
0.103.0
```

## Create a new cluster

* Create `kubernetes-admin` AWS IAM User with programmatic access only
  * Assign policies `AdministratorAccess`, `IAMUserChangePassword`
  * Keep the access/secret for this user

Login to AWS with the `kubernetes-admin` access/secret under profile `dfc-kubernetes-admin`

```
aws configure --profile dfc-kubernetes-admin
```

Set the profile in env var

```
export AWS_PROFILE=dfc-kubernetes-admin
```

Verify you are connected

```
$ aws sts get-caller-identity
{
    "UserId": "AIDA5BVA4UFWBF6VZNG67",
    "Account": "896911843692",
    "Arn": "arn:aws:iam::896911843692:user/kubernetes-admin"
}
```

Set the cluster name you want to create in an env var

```
CLUSTER_NAME=main
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
sudo mkdir -p /etc/dfc/k8s/${CLUSTER_NAME} && sudo chown $USER -R /etc/dfc/k8s/${CLUSTER_NAME}
```

Create a kubeconfig file

```
export KUBECONFIG=/etc/dfc/k8s/${CLUSTER_NAME}/.kubeconfig
eksctl utils write-kubeconfig --region $AWS_REGION --cluster "${CLUSTER_NAME}" --kubeconfig "${KUBECONFIG}"
```

Verify connection to the cluster

```
kubectl get nodes
```

Create a .env file for the cluster:

```
echo "export CLUSTER_NAME=${CLUSTER_NAME}
export AWS_PROFILE=${AWS_PROFILE}
export AWS_REGION=${AWS_REGION}
export KUBECONFIG=/etc/dfc/k8s/${CLUSTER_NAME}/.kubeconfig" > clusters/${CLUSTER_NAME}/.env
```

Deploy the Nginx ingress: `kubectl apply -k apps/ingress-nginx`

Verify that ingress was deployed: `kubectl -n ingress-nginx get pods`

Get the ingress hostname: `kubectl -n ingress-nginx get service ingress-nginx-controller`

Set a DNS CNAME: `k8s-main-ingress.dataforchange.org.il` to this hostname

Write this domain for reference in `clusters/${CLUSTER_NAME}/ingress-domain.txt`

Deploy Vault: `kubectl apply -k apps/vault`

Initialize and set the unseal keys, see `apps/vault/kustomization.yaml` for the required secret and uncomment the patch

Redeploy vault and check that it's unsealed automatically on startup

Initialize Vault as needed

Store the .kubeconfig file from `/etc/dfc/k8s/main/.kubeconfig` in vault under `admin/k8s-main-kubeconfig` in key `KUBECONFIG`

## Deploy ArgoCD

Register an oauth app in github (https://github.com/organizations/data-for-change/settings/applications):
* application name: `argocd`
* homepage url: `https://argocd.dataforchange.org.il`
* authorization callback url: `https://argocd.dataforchange.org.il/api/dex/callback`
* store the client id and secret in vault `projects/k8s/argocd/github-oauth` keys `client_id` and `client_secret`

Create github teams under data-for-change organization (https://github.com/orgs/data-for-change/teams):
* `argocd-admins`
* `argocd-users`

Create namespace: `kubectl create ns argocd`

Login to Vault as admin and add the following:

`readonly` policy:

```
path "kv/data/*" {
  capabilities = [ "read" ]
}
```

approle:

```
vault write auth/approle/role/argocd token_policies="readonly" token_ttl=1h token_max_ttl=4h
```

Get role and secret id

```
vault read auth/approle/role/argocd/role-id
vault write -force auth/approle/role/argocd/secret-id
``` 

Create vault credentials secret

```
kubectl -n argocd create secret generic argocd-vault-plugin-credentials \
    --from-literal=VAULT_ADDR= \
    --from-literal=AVP_TYPE=vault \
    --from-literal=AVP_AUTH_TYPE=approle \
    --from-literal=AVP_ROLE_ID= \
    --from-literal=AVP_SECRET_ID=
```

Set Vault connection details with admin token:

```
export VAULT_ADDR=https://vault.dataforchange.org.il
export VAULT_TOKEN=
```

Make sure you have `vault` and `jq` binaries installed locally

Render the templates with secret values from Vault

```
apps/argocd-install/render_templates.sh
```

Deploy: `kubectl -n argocd apply -k apps/argocd-install`

## Deploy Velero

Follow the instructions in `apps/velero/README.md`

Deploy scheduled backup: `kubectl apply -k apps/velero-backups`