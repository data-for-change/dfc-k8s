# Modifying the cluster

## Scaling cluster nodes

Modify the nodegroup configuration in `clusters/CLUSTER_NAME/eks-cluster.yaml` and run:

```bash
eksctl scale nodegroup -f clusters/CLUSTER_NAME/eks-cluster.yaml
```
