#!/usr/bin/env bash
HELP_MESSAGE="
Migrate data from a local path to a PVC in AWS
Requires kubectl connected to target cluster

the last source_path path part will be created inside the target pvc, for example,
if source_path is '/foo/bar', the pvc will contain a subdirectory named 'bar' with the
data from '/foo/bar' inside it.
"

set -e

SOURCE_PATH="${1}"
TARGET_PVC_NAMESPACE="${2}"
TARGET_PVC_NAME="${3}"
TARGET_PVC_STORAGE="${4}"

if [[ -z "${SOURCE_PATH}" || -z "${TARGET_PVC_NAMESPACE}" || -z "${TARGET_PVC_NAME}" \
      || -z "${TARGET_PVC_STORAGE}" ]]; then
  echo "Usage: $0 <source_path> <target_pvc_namespace> <target_pvc_name> <target_pvc_storage>"
  echo "${HELP_MESSAGE}"
  exit 1
fi

if [[ ! -d "${SOURCE_PATH}" ]]; then
  echo "Source path ${SOURCE_PATH} does not exist"
  exit 1
fi

cat <<EOF
Source path: ${SOURCE_PATH}
Target PVC: ${TARGET_PVC_NAMESPACE}/${TARGET_PVC_NAME} (${TARGET_PVC_STORAGE})
EOF

echo "apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ${TARGET_PVC_NAME}
  namespace: ${TARGET_PVC_NAMESPACE}
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: ${TARGET_PVC_STORAGE}
" | kubectl apply -f -

echo "apiVersion: apps/v1
kind: Deployment
metadata:
  name: migrate-data-${TARGET_PVC_NAME}
  namespace: ${TARGET_PVC_NAMESPACE}
spec:
  selector:
    matchLabels:
      app: migrate-data-${TARGET_PVC_NAME}
  replicas: 1
  revisionHistoryLimit: 2
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: migrate-data-${TARGET_PVC_NAME}
    spec:
      terminationGracePeriodSeconds: 1
      containers:
      - name: alpine
        image: alpine@sha256:bc41182d7ef5ffc53a40b044e725193bc10142a1243f395ee852a8d9730fc2ad
        command:
          - sh
          - -c
          - while true; do sleep 86400; done
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: ${TARGET_PVC_NAME}
" | kubectl apply -f -

kubectl rollout status deployment/migrate-data-${TARGET_PVC_NAME} -n ${TARGET_PVC_NAMESPACE}

POD_NAME=$(kubectl get pod -n ${TARGET_PVC_NAMESPACE} -l app=migrate-data-${TARGET_PVC_NAME} -o jsonpath="{.items[0].metadata.name}")

echo "Copying data from ${SOURCE_PATH} to ${TARGET_PVC_NAMESPACE}/${TARGET_PVC_NAME}..."
cd "${SOURCE_PATH}"
tar cf - . | kubectl exec -c alpine -i -n "${TARGET_PVC_NAMESPACE}" "${POD_NAME}" -- tar xf - -C /data

kubectl exec -it -n ${TARGET_PVC_NAMESPACE} ${POD_NAME} -- sh -c "ls -lah /data"

kubectl delete deployment/migrate-data-${TARGET_PVC_NAME} -n ${TARGET_PVC_NAMESPACE}

echo Great Success
