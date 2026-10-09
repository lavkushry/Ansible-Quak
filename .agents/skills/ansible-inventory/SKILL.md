---
name: ansible-inventory
description: >
  Use when creating, editing, or reviewing Ansible inventory files,
  group variables, host variables, or dynamic inventory configurations.
---

# Ansible Inventory Deep-Dive Guide

## Mandatory Pre-Steps
1. Decide if the inventory should be static (YAML) or dynamic (Plugin).
2. NEVER use INI format for complex modern Ansible deployments; standard is YAML.
3. Group logically by environment (dev/prod), region (us-east/eu-west), and role (web/db).

---

## 1. YAML Inventory Format Complete Reference

YAML is strictly nested. Avoid hallucinating INI patterns like `[webservers:children]`.

```yaml
all:
  vars:
    ansible_user: admin
  children:
    production:
      children:
        webservers:
          hosts:
            web01.example.com:
              ansible_host: 192.168.1.10
              max_clients: 200
            web02.example.com:
              ansible_host: 192.168.1.11
        dbservers:
          hosts:
            db01.example.com:
              ansible_host: 192.168.1.20
    staging:
      hosts:
        stage-web.example.com:
```

---

## 2. Special Groups

- **`all`**: Automatically includes every host in the inventory.
- **`ungrouped`**: Automatically includes any host not belonging to any other group except `all`.

---

## 3. Directory Layout for Vars

Do NOT stuff all variables into the `inventory.yml` file. Use directory structures.

```text
inventory/
  production/
    hosts.yml
    group_vars/
      all.yml          # Applies to all prod hosts
      webservers.yml   # Applies to prod webservers
    host_vars/
      web01.example.com.yml
  staging/
    hosts.yml
    ...
```

---

## 4. Host Patterns & Targeting

When running `ansible-playbook -i hosts.yml playbook.yml --limit <pattern>`:

- **All hosts in a group**: `webservers`
- **Multiple groups (OR)**: `webservers:dbservers`
- **Intersection (AND)**: `webservers:&production` (Hosts in BOTH groups)
- **Exclusion (NOT)**: `webservers:!staging` (Hosts in webservers but NOT in staging)
- **Wildcards**: `*.example.com`, `web*`
- **Regex**: `~^web[0-9]+\.example\.com$`
- **Slices**: `webservers[0:2]` (First two hosts)

---

## 5. Dynamic Inventory Plugins

For cloud environments, use dynamic plugins instead of static IPs.

### AWS (`amazon.aws.aws_ec2`)
```yaml
plugin: amazon.aws.aws_ec2
regions:
  - us-east-1
keyed_groups:
  - prefix: env
    key: tags.Environment
```

### Azure (`azure.azcollection.azure_rm`)
```yaml
plugin: azure.azcollection.azure_rm
include_vm_resource_groups:
  - myResourceGroup
```

### GCP (`google.cloud.gcp_compute`)
```yaml
plugin: google.cloud.gcp_compute
projects:
  - my-gcp-project
auth_kind: serviceaccount
```

### Constructed Plugin (`ansible.builtin.constructed`)
Useful for dynamically creating groups from existing facts or other inventory plugins.
```yaml
plugin: ansible.builtin.constructed
strict: False
groups:
  ubuntu_servers: "ansible_distribution == 'Ubuntu'"
```

---

## 6. Crucial Connection Variables

Place these in host or group definitions:
- `ansible_host`: The actual IP/FQDN to connect to.
- `ansible_port`: SSH/WinRM port.
- `ansible_user`: Connection user.
- `ansible_connection`: `ssh`, `winrm`, `local`, `docker`.
- `ansible_become`: `true` / `false`.
- `ansible_become_method`: `sudo`, `su`, `pbrun`.
- `ansible_ssh_private_key_file`: Path to the PEM key.

---

## 7. Anti-Hallucination: INI vs YAML

Do NOT mix syntaxes. If you are writing a YAML file (`.yml`), this is completely invalid:
```yaml
[webservers]
web01

[webservers:vars]
foo=bar
```
Use proper YAML dictionaries (see Section 1).
