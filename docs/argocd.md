# Argo CD - continuous deployment

All the infrastructure is managed via apps defined under [/apps](/apps).
Each directory under [/apps](/apps) is a single app which can be deployed to the cluster.
Apps are usually helm charts, but can also contain manifests or kustomize files.

App definitions are defined in the following files:
* Apps: [/apps/argocd-apps/values-prod-apps.yaml](/apps/argocd-apps/values-prod-apps.yaml)
* Projects: [/apps/argocd-apps/values-prod-projects.yaml](/apps/argocd-apps/values-prod-projects.yaml)
* Infrastructure Apps: [/apps/argocd-apps/values-prod-infra-apps.yaml](/apps/argocd-apps/values-prod-infra-apps.yaml)

Any change in those files which is merged to main branch will be continuously deployed to the cluster.

You can disable the auto-sync of apps, allowing to view diff before applying or 
to make manual changes for debugging, by adding `disableAutoSync: true` to the 
relevant app definition.

You can track progress of deployments using the Web UI.
Login at https://argocd.dataforchange.org.il using GitHub.
To have access you need to belong to one of these teams:
* [argocd-users](https://github.com/orgs/data-for-change/teams/argocd-users) - have read-only access, can view deployment progress but can't perform any actions 
* [argocd-admins](https://github.com/orgs/data-for-change/teams/argocd-admins) - have full admin access

## Using values from Vault

ArgoCD plugin handles replacing values in rendered templates from our Vault.
Any value in the following format will be replaced:

* `vault:path:key` - the `key` will be taken from the Vault `path`, value will be base64 encoded and should be used in k8s secrets only

## Making Changes Locally

To make changes locally without depending on argocd, use the following procedure:

* Prerequisites:
  * Python3
  * `pip install kubernetes`
* Connect to the cluster
  * Verify by running `kubectl get nodes` and make sure you see the relevant cluster nodes
* Disable auto-sync for relevant app so your changes won't be rollbacked:
  * set `disableAutoSync: true` for the relevant app at `hasadna-argocd/values-hasadna.yaml`
  * Commit & Push this change
* Set the chart path, name and value files in env vars, for example:
  * `CHART_NAME=monitoring`
  * `CHART_PATH=apps/monitoring/`
  * `CHART_NAMESPACE=monitoring`
  * `HELM_ARGS="-f values-main.yaml"`
* Render the chart yamls without applying:
  * `bin/render_chart.sh $CHART_PATH $CHART_NAME $CHART_NAMESPACE "${HELM_ARGS}"`
* Dry run the kubectl apply on the server, to see which objects would be modified:
  * Note that argocd adds some labels, so it may detect these changes in all objects 
  * `bin/render_chart.sh $CHART_PATH $CHART_NAME $CHART_NAMESPACE "${HELM_ARGS}"` 
* Apply the chart to the cluster:
  * `bin/render_chart.sh $CHART_PATH $CHART_NAME $CHART_NAMESPACE "${HELM_ARGS}"`

## Using ArgoCD CLI

[Download ArgoCD CLI](https://argo-cd.readthedocs.io/en/stable/getting_started/#2-download-argo-cd-cli)

Login using SSO: `argocd login --sso argocd-grpc.dataforchange.org.il`
