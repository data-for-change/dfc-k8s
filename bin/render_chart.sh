#!/usr/bin/env bash

CHART_PATH="${1}"
CHART_NAME="${2}"
CHART_NAMESPACE="${3}"
HELM_ARGS="${4}"
APPLY="${5}"

init() {
  python3 apps/argocd-install/argocd-dfc-plugin.py init $CHART_PATH
}

render() {
  python3 apps/argocd-install/argocd-dfc-plugin.py generate $CHART_PATH $CHART_NAME $CHART_NAMESPACE $HELM_ARGS
}

if [ "${APPLY}" == "--apply" ]; then
  init && render | kubectl apply -f -
elif [ "${APPLY}" == "--dry-run" ]; then
  init && render | kubectl apply --dry-run=server -f -
else
  init && render
fi
