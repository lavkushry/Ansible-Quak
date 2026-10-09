---
name: ansible-module-reference
description: >
  Quick reference for the 50 most commonly used Ansible modules with their
  FQCN, collection, key parameters, and usage examples. Consult this BEFORE
  using any module to verify it exists and get correct parameter names.
---

# Ansible Module Quick Reference

Consult this table BEFORE using any module to verify it exists and get the correct Fully Qualified Collection Name (FQCN) and parameter names.

## `ansible.builtin` (Always available, no requirements needed)

| Module | Purpose | Key Parameters | Example |
|--------|---------|----------------|----------|
| `ansible.builtin.apt` | Debian packages | `name`, `state`, `update_cache`, `cache_valid_time` | `apt: name=nginx state=present` |
| `ansible.builtin.dnf` | RHEL packages | `name`, `state`, `enablerepo` | `dnf: name=httpd state=latest` |
| `ansible.builtin.package` | Generic OS packages | `name`, `state` | `package: name=git state=present` |
| `ansible.builtin.pip` | Python packages | `name`, `state`, `virtualenv` | `pip: name=requests state=present` |
| `ansible.builtin.copy` | Copy files | `src`, `dest`, `owner`, `group`, `mode` | `copy: src=file dest=/opt/file mode='0644'` |
| `ansible.builtin.template` | Jinja2 templates | `src`, `dest`, `owner`, `group`, `mode`, `validate` | `template: src=app.j2 dest=/etc/app.conf` |
| `ansible.builtin.file` | File state/perms | `path`, `state`, `owner`, `group`, `mode` | `file: path=/etc/dir state=directory` |
| `ansible.builtin.lineinfile` | File text lines | `path`, `regexp`, `line`, `state` | `lineinfile: path=/etc/hosts line='127.0.0.1 localhost'` |
| `ansible.builtin.service` | Manage services | `name`, `state`, `enabled` | `service: name=sshd state=restarted enabled=true` |
| `ansible.builtin.systemd` | Manage systemd | `name`, `state`, `enabled`, `daemon_reload` | `systemd: name=nginx state=started` |
| `ansible.builtin.user` | Manage users | `name`, `state`, `groups`, `password`, `shell` | `user: name=deploy state=present` |
| `ansible.builtin.group` | Manage groups | `name`, `state`, `gid` | `group: name=docker state=present` |
| `ansible.builtin.command` | Run commands | `cmd`, `creates`, `removes`, `chdir` | `command: /opt/bin/script.sh` |
| `ansible.builtin.shell` | Run shell cmd | `cmd`, `creates`, `removes`, `chdir` | `shell: echo "$VAR" > /tmp/out` |
| `ansible.builtin.cron` | Manage cron jobs | `name`, `minute`, `hour`, `job`, `state` | `cron: name="backup" minute="0" job="/opt/backup.sh"` |

## `ansible.posix` (Requires ansible.posix collection)

| Module | Purpose | Key Parameters | Example |
|--------|---------|----------------|----------|
| `ansible.posix.firewalld` | Firewall rules | `service`, `port`, `zone`, `state`, `permanent`, `immediate` | `firewalld: service=http state=enabled permanent=true immediate=true` |
| `ansible.posix.seboolean` | SELinux booleans | `name`, `state`, `persistent` | `seboolean: name=httpd_can_network_connect state=true persistent=true` |
| `ansible.posix.authorized_key` | SSH keys | `user`, `key`, `state` | `authorized_key: user=root key="{{ lookup('file', 'pubkey') }}"` |
| `ansible.posix.sysctl` | Kernel params | `name`, `value`, `sysctl_set`, `state` | `sysctl: name=net.ipv4.ip_forward value=1 state=present` |
| `ansible.posix.mount` | Mount points | `path`, `src`, `fstype`, `state`, `opts` | `mount: path=/mnt src=/dev/sdb1 fstype=ext4 state=mounted` |
| `ansible.posix.acl` | File ACLs | `path`, `entity`, `etype`, `permissions`, `state` | `acl: path=/etc/secret entity=deploy etype=user permissions=r state=present` |

## `community.general` (Requires community.general collection)

| Module | Purpose | Key Parameters | Example |
|--------|---------|----------------|----------|
| `community.general.ufw` | UFW firewall | `rule`, `port`, `proto`, `direction`, `state` | `ufw: rule=allow port=22 proto=tcp` |
| `community.general.timezone` | Timezone | `name` | `timezone: name=UTC` |
| `community.general.hostname` | Hostname | `name` | `hostname: name=webserver01` |
| `community.general.ini_file` | INI files | `path`, `section`, `option`, `value`, `state` | `ini_file: path=config.ini section=Main option=Debug value=true` |
| `community.general.nmcli` | NetworkManager | `conn_name`, `type`, `ip4`, `gw4`, `dns4`, `state` | `nmcli: conn_name=eth0 type=ethernet ip4=192.168.1.10/24 state=present` |

## `community.docker` (Requires community.docker collection)

| Module | Purpose | Key Parameters | Example |
|--------|---------|----------------|----------|
| `community.docker.docker_container` | Containers | `name`, `image`, `state`, `ports`, `volumes`, `env` | `docker_container: name=redis image=redis:alpine state=started` |
| `community.docker.docker_image` | Images | `name`, `source`, `build`, `tag`, `state` | `docker_image: name=my_app source=build build={path: '/src'}` |
| `community.docker.docker_network` | Networks | `name`, `state`, `driver` | `docker_network: name=app_net state=present` |
| `community.docker.docker_compose_v2` | Compose Stacks | `project_src`, `state`, `pull`, `recreate` | `docker_compose_v2: project_src=/opt/app state=present` |

## `community.mysql` (Requires community.mysql collection)

| Module | Purpose | Key Parameters | Example |
|--------|---------|----------------|----------|
| `community.mysql.mysql_db` | Databases | `name`, `state`, `login_user`, `login_password` | `mysql_db: name=app_db state=present` |
| `community.mysql.mysql_user` | Users | `name`, `password`, `priv`, `state`, `host` | `mysql_user: name=app_user password=secret priv=app_db.*:ALL state=present` |

## `community.postgresql` (Requires community.postgresql collection)

| Module | Purpose | Key Parameters | Example |
|--------|---------|----------------|----------|
| `community.postgresql.postgresql_db` | Databases | `name`, `state`, `owner` | `postgresql_db: name=app_db state=present` |
| `community.postgresql.postgresql_user` | Users | `name`, `password`, `db`, `priv`, `state` | `postgresql_user: name=app_user password=secret state=present` |

## `amazon.aws` (Requires amazon.aws collection)

| Module | Purpose | Key Parameters | Example |
|--------|---------|----------------|----------|
| `amazon.aws.ec2_instance` | EC2 | `name`, `instance_type`, `image_id`, `state`, `wait` | `ec2_instance: name=web instance_type=t3.micro state=started` |
| `amazon.aws.ec2_security_group` | SG | `name`, `description`, `vpc_id`, `rules` | `ec2_security_group: name=web_sg rules=[{proto: tcp, ports: [80]}]` |
| `amazon.aws.s3_bucket` | S3 | `name`, `state`, `tags` | `s3_bucket: name=my-bucket state=present` |
| `amazon.aws.s3_object` | S3 Object | `bucket`, `object`, `src`, `mode` | `s3_object: bucket=my-bucket object=file.txt src=/tmp/file.txt mode=put` |
| `amazon.aws.iam_role` | IAM | `name`, `assume_role_policy_document`, `state` | `iam_role: name=EC2Role assume_role_policy_document=...` |

## How to Verify Before Using

If you are unsure of a module's name, its collection, or its parameters, always verify locally:

```bash
# Check if a module exists and read its documentation
ansible-doc community.general.ufw

# List all modules in a specific collection
ansible-doc -l -t module | grep community.general

# Get only the parameters (JSON output)
ansible-doc community.general.ufw --json | python -m json.tool
```
