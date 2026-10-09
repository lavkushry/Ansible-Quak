---
name: ansible-role
description: >
  MANDATORY skill for creating, modifying, or reviewing Ansible roles.
  Enforces galaxy structure, variable precedence, idempotency, and testing.
---

# Ansible Role Development Guide

## Complete Role Scaffolding

An Ansible role should follow the standard Galaxy structure:

```
my_role/
├── defaults/
│   └── main.yml        # Lowest priority variables (user defaults)
├── files/              # Static files to be copied to targets
├── handlers/
│   └── main.yml        # Handlers triggered by tasks
├── meta/
│   └── main.yml        # Role metadata and dependencies
├── tasks/
│   ├── main.yml        # Main entrypoint for tasks
│   ├── install.yml     # Modularized task file example
│   ├── configure.yml
│   └── service.yml
├── templates/          # Jinja2 templates (.j2)
├── tests/              # (or molecule/) Test configurations
├── vars/
│   └── main.yml        # High priority variables (internal/constants)
└── README.md           # Documentation
```

### Splitting Tasks

`tasks/main.yml` should act as an orchestrator:

```yaml
---
# tasks/main.yml
- ansible.builtin.import_tasks: install.yml
- ansible.builtin.import_tasks: configure.yml
- ansible.builtin.import_tasks: service.yml
```

## Variable Precedence Deep Dive

Ansible resolves variables through a 22-level precedence hierarchy (lowest to highest):

1. command line values (for example, `-u my_user`)
2. **role defaults (`roles/x/defaults/main.yml`)** -> Use for values users *should* override.
3. inventory file or script group vars
4. inventory group_vars/all
5. playbook group_vars/all
6. inventory group_vars/*
7. playbook group_vars/*
8. inventory file or script host vars
9. inventory host_vars/*
10. playbook host_vars/*
11. host facts / cached set_facts
12. play vars
13. play vars_prompt
14. play vars_files
15. **role vars (`roles/x/vars/main.yml`)** -> Use for values users *should not* override (constants).
16. block vars (only for tasks in block)
17. task vars (only for the task)
18. include_vars
19. set_facts / registered vars
20. role (and include_role) params
21. include params
22. extra vars (`-e`) -> Highest precedence, usually for testing or CI.

**Guidance**: Put user-configurable values in `defaults/` (level 2). Put internal constants in `vars/` (level 15). Never put secrets in either — use ansible-vault.

## Role Design Patterns

- **Single-responsibility roles**: A role should do one thing well (e.g., install Nginx), not configure the whole server.
- **Platform-agnostic roles**: Use `ansible_os_family` to support multiple OSes.
  ```yaml
  - ansible.builtin.include_tasks: "install_{{ ansible_os_family | lower }}.yml"
  ```
- **Feature flags**: Use booleans in defaults to toggle features.
  ```yaml
  # defaults/main.yml
  my_role_enable_monitoring: false
  
  # tasks/main.yml
  - ansible.builtin.include_tasks: monitoring.yml
    when: my_role_enable_monitoring | bool
  ```
- **Dependencies**: Declare required roles in `meta/main.yml`.

## Meta/main.yml Complete Template

```yaml
---
galaxy_info:
  role_name: my_role
  namespace: my_org
  author: Your Name
  description: What this role does
  company: Your Company
  license: MIT
  min_ansible_version: "2.15"
  platforms:
    - name: Ubuntu
      versions: ['jammy', 'noble']
    - name: EL
      versions: ['8', '9']
  galaxy_tags:
    - web
    - nginx

collections:
  - name: ansible.builtin
  - name: community.general
  - name: ansible.posix

dependencies:
  - role: common
  # - role: geerlingguy.docker
```

## Molecule Testing Complete Setup

Use Molecule to test roles via containers or VMs.

**molecule/default/molecule.yml**
```yaml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: "geerlingguy/docker-ubuntu2204-ansible:latest"
    command: ""
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
    privileged: true
    pre_build_image: true
provisioner:
  name: ansible
verifier:
  name: ansible
```

**molecule/default/converge.yml**
```yaml
---
- name: Converge
  hosts: all
  tasks:
    - name: "Include my_role"
      ansible.builtin.include_role:
        name: "my_role"
```

**molecule/default/verify.yml**
```yaml
---
- name: Verify
  hosts: all
  tasks:
    - name: Check if service is running
      ansible.builtin.command: systemctl is-active my_service
      register: service_status
      changed_when: false
    
    - name: Assert service is running
      ansible.builtin.assert:
        that:
          - service_status.rc == 0
```

## README.md Template for Roles

```markdown
# Role Name

Brief description of the role.

## Requirements

Any pre-requisites that may not be covered by Ansible itself or the role.

## Role Variables

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| `role_var_1`  | `false`       | Does X.     |

## Dependencies

A list of other roles hosted on Galaxy should go here.

## Example Playbook

```yaml
- hosts: servers
  roles:
     - { role: username.rolename, role_var_1: true }
```

## License

MIT / BSD

## Author Information

An optional section for the role authors to include contact information.
```

## Anti-Hallucination for Roles

- Roles DO NOT have `playbooks/` directories.
- Role tasks DO NOT have `hosts:` — that's playbook syntax.
- `handlers` ARE NOT tasks — they only fire on notification.
- `vars/` is NOT the same as `defaults/` — precedence matters immensely.
- `meta/main.yml` dependencies use role names, not playbook paths.
