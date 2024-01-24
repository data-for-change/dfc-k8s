#!/usr/bin/env python3
import sys
import time
import json
import subprocess


MIGRATION_OBJECTS_PREFIX = 'k8s-docker-migration'
SNAPSHOTS_VELERO_BACKUP = 'k8s-docker-migration'
MAIN_VOLUME_NAME = 'main-docker'
VOLUMES = [
    {
        'namespace': 'anyway',
        'name': 'airflow-db',
        'target_path': '/anyway/airflow-db'
    },
    {
        'namespace': 'anyway',
        'name': 'airflow-etl-data',
        'target_path': '/anyway/airflow-etl-data'
    },
    {
        'namespace': 'anyway',
        'name': 'airflow-home-data',
        'target_path': '/anyway/airflow-home-data'
    },
    {
        'namespace': 'anyway',
        'name': 'db2',
        'target_path': '/anyway/db'
    },
    {
        'namespace': 'cluster-admin',
        'name': 'terraform-state-db',
        'target_path': '/terraform-state-db'
    },
    {
        'namespace': 'vault',
        'name': 'vault',
        'target_path': '/vault'
    },
    {
        'namespace': 'redash',
        'name': 'postgres',
        'target_path': '/redash-postgres'
    },
]


def find_snapshot_by_tags(tags):
    filters = ' '.join([f'Name=tag:{key},Values={value}' for key, value in tags.items()])
    snapshots = json.loads(subprocess.check_output(
        f'aws --no-cli-pager ec2 describe-snapshots --filters {filters}', shell=True
    ))['Snapshots']
    assert len(snapshots) == 1
    return snapshots[0]['SnapshotId']


def create_volume_from_snapshot_id(snapshot_id, volume_name, availability_zone='eu-central-1b', volume_type='gp2'):
    # check if volume already exists
    if len(json.loads(subprocess.check_output(
        f'aws --no-cli-pager ec2 describe-volumes --filters Name=tag:Name,Values={volume_name}', shell=True
    ))['Volumes']) > 0:
        print(f'Volume {volume_name} already exists')
        return
    subprocess.check_call(
        f'aws --no-cli-pager ec2 create-volume --snapshot-id {snapshot_id} --availability-zone {availability_zone} --volume-type {volume_type} --tag-specifications "ResourceType=volume,Tags=[{{Key=Name,Value={volume_name}}}]"',
        shell=True
    )


def create_volume_from_snapshot(namespace, name):
    volume_name = f'{MIGRATION_OBJECTS_PREFIX}-{namespace}-{name}'
    create_volume_from_snapshot_id(
        find_snapshot_by_tags({
            'velero.io/backup': SNAPSHOTS_VELERO_BACKUP,
            'kubernetes.io/created-for/pvc/namespace': namespace,
            'kubernetes.io/created-for/pvc/name': name
        }),
        volume_name
    )
    return volume_name


def create_all_volumes_from_snapshots():
    pending_volume_names = set()
    for volume in VOLUMES:
        pending_volume_names.add(create_volume_from_snapshot(volume['namespace'], volume['name']))
    while len(pending_volume_names) > 0:
        print(f'Waiting for volumes to be available: {pending_volume_names}')
        time.sleep(5)
        for volume_name in pending_volume_names.copy():
            volume = get_volume(volume_name)
            if volume['State'] == 'available':
                pending_volume_names.remove(volume_name)
                print(f'Volume {volume_name} is available')


def get_volume(name):
    volumes = json.loads(subprocess.check_output(
        f'aws --no-cli-pager ec2 describe-volumes --filters Name=tag:Name,Values={name}', shell=True
    ))['Volumes']
    assert len(volumes) == 1
    return volumes[0]


def mount_volume(migration_server_ip, volume_name):
    volume = get_volume(volume_name)
    assert len(volume['Attachments']) == 1
    device = volume['Attachments'][0]['Device']
    device = device.replace('/dev/sd', '/dev/xvd')
    subprocess.check_call(
        [
            'ssh', f'ubuntu@{migration_server_ip}', f'''
                sudo umount {device}
                sudo mkdir -p /mnt/{volume_name}
                sudo mount {device} /mnt/{volume_name}
                echo "Volume {volume_name} is mounted at /mnt/{volume_name}"
            '''
        ]
    )


def mount_all_volumes(migration_server_ip):
    for volume in VOLUMES:
        mount_volume(migration_server_ip, f'{MIGRATION_OBJECTS_PREFIX}-{volume["namespace"]}-{volume["name"]}')
    mount_volume(migration_server_ip, MAIN_VOLUME_NAME)


def migrate_volume(migration_server_ip, volume_name, target_path):
    subprocess.check_call(
        [
            'ssh', f'ubuntu@{migration_server_ip}', f'''
                sudo mkdir -p /mnt/{MAIN_VOLUME_NAME}{target_path}
                sudo rsync -a /mnt/{volume_name}/ /mnt/{MAIN_VOLUME_NAME}{target_path}
            '''
        ]
    )
    print(f'Volume {volume_name} was migrated to {MAIN_VOLUME_NAME}{target_path}')


def migrate_all_volumes(migration_server_ip):
    for volume in VOLUMES:
        volume_name = f'{MIGRATION_OBJECTS_PREFIX}-{volume["namespace"]}-{volume["name"]}'
        target_path = volume['target_path']
        print(f'Migrating volume {volume_name} to {target_path}')
        migrate_volume(migration_server_ip, volume_name, target_path)
        print("OK")


def main(cmd, *args):
    res = globals()[cmd](*args)
    if res is not None:
        print(res)


if __name__ == '__main__':
    main(*sys.argv[1:])
