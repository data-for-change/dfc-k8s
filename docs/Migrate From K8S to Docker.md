# Migrate from K8S to Docker

## Prerequisites

* Install AWS CLI
* Install Vault CLI
* Set env vars for AWS and Vault credentials

## Migrate

* Terminate all workloads
* Create volumes for each snapshot: `bin/migrate_k8s_to_docker.py create_all_volumes_from_snapshots`
* Create an EC2 instance for migration
* Attach the volumes to the instance
* Mount all the volumes: `bin/migrate_k8s_to_docker.py MIGRATION_SERVER_IP mount_all_volumes`
* Run the volumes migration script: `bin/migrate_k8s_to_docker.py MIGRATION_SERVER_IP migrate_all_volumes`
* Remove the EC2 instance and all the volumes except the main volume
* Create new EC2 instance for the docker compose environment:
  * Instance type: m6a.large (2 vCPU, 8GB RAM)
  * OS: Ubuntu 22.04
  * Root volume: 100GB
  * Attach the main volume to the instance, note the device name
* SSH to the instance: 

```
# mount the main volume
echo "DEVICE_NAME /data ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo mkdir /data
sudo mount -a

# install Docker
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker

# set logging driver + rotation
sudo mkdir -p /etc/docker
echo '{"log-driver": "local", "log-opts": {"max-size": "100m", "max-file": "10"}}' | sudo tee /etc/docker/daemon.json

# Create ssh key
ssh-keygen -t ed25519 -C "dfc-main-docker"

# Add this key to GitHub dfc-k8s repo deploy keys without write access and clone
cd ~
git clone git@github.com:data-for-change/dfc-k8s.git
git checkout migrate-to-docker-compose

# Install the apps according to each app's README.md
# If the app doesn't have details, just run:
cd ~/dfc-k8s
( cd apps/APP_NAME && docker compose up -d )
```
