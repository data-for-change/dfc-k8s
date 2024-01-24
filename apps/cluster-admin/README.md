# Cluster Admin

## Terraform State DB

### Install

```
bin/render_env_template.py apps/cluster-admin/secrets/terraform-state-db.env.template > apps/cluster-admin/secrets/terraform-state-db.env
vault kv get -format=json kv/projects/iac/terraform | jq -r '.data.data["state_db_server.key"]' > apps/cluster-admin/secrets/state_db_server.key
vault kv get -format=json kv/projects/iac/terraform | jq -r '.data.data["state_db_server.crt"]' > apps/cluster-admin/secrets/state_db_server.crt
```
