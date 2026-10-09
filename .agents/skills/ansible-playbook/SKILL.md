---
name: ansible-playbook
description: >
  MANDATORY skill for creating, editing, or reviewing ANY Ansible playbook.
  Prevents hallucinated modules, enforces FQCN, and ensures production-grade quality.
---

# Ansible Playbook Development Guide

## Mandatory Pre-Steps (Before Writing ANY Code)
1. Read `requirements.yml` — extract exact collection names and versions
2. Read existing `playbooks/` for naming conventions and patterns
3. Read `inventories/` to understand target groups
4. Read `ansible.cfg` for project settings
5. If referencing a module, run `ansible-doc <FQCN>` to verify it exists AND get real parameters

## Playbook Structure Template

Always use the following structure for new playbooks to ensure consistency, safety, and readability:

```yaml
---
# Playbook: <descriptive_name>
# Purpose: <what this playbook achieves>
# Target: <which inventory groups>
# Author: <name>
# Date: <date>

- name: <Play description starting with verb>
  hosts: <group_name>
  become: true
  gather_facts: true
  any_errors_fatal: true  # Recommended for critical infrastructure
  
  vars_files:
    - vars/main.yml
  
  pre_tasks:
    - name: Validate required variables
      ansible.builtin.assert:
        that:
          - required_var is defined
          - required_var | length > 0
        fail_msg: "Required variable 'required_var' is not set"
      tags: ['always', 'preflight']
  
  roles:
    - role: my_role
      tags: ['my_role']
  
  tasks:
    - name: Task description
      ansible.builtin.module_name:
        param: value
      tags: ['category']
  
  post_tasks:
    - name: Verification step
      ansible.builtin.uri:
        url: "http://{{ ansible_host }}:{{ app_port }}/health"
        status_code: 200
      tags: ['verify']
  
  handlers:
    - name: Restart service_name
      ansible.builtin.systemd_service:
        name: service_name
        state: restarted
        daemon_reload: true
      become: true
```

## Module Decision Tree

When you need to accomplish a task, follow this decision tree to find the correct module:

**Need to install packages?**
├── Debian/Ubuntu → `ansible.builtin.apt`
│   Parameters: `name`, `state(present/absent/latest)`, `update_cache`, `cache_valid_time`
├── RHEL/CentOS → `ansible.builtin.dnf` (NOT yum for RHEL 8+)
│   Parameters: `name`, `state`, `enablerepo`, `disablerepo`
├── Any distro → `ansible.builtin.package` (auto-detects)
│   Parameters: `name`, `state`
└── Python packages → `ansible.builtin.pip`
    Parameters: `name`, `state`, `virtualenv`, `virtualenv_python`

**Need to manage files?**
├── Copy local → remote: `ansible.builtin.copy`
│   Parameters: `src`, `dest`, `owner`, `group`, `mode`, `backup`, `content(for inline)`
├── Template → remote: `ansible.builtin.template`
│   Parameters: `src`, `dest`, `owner`, `group`, `mode`, `backup`, `validate`
├── Download URL → remote: `ansible.builtin.get_url`
│   Parameters: `url`, `dest`, `checksum`, `mode`, `owner`, `group`, `timeout`
├── Set permissions/ownership: `ansible.builtin.file`
│   Parameters: `path`, `state(file/directory/link/absent/touch)`, `owner`, `group`, `mode`, `recurse`
├── Edit line in file: `ansible.builtin.lineinfile`
│   Parameters: `path`, `line`, `regexp`, `state`, `insertafter`, `insertbefore`, `backup`
├── Edit block in file: `ansible.builtin.blockinfile`
│   Parameters: `path`, `block`, `marker`, `insertafter`, `insertbefore`, `state`
└── Archive/Extract: `ansible.builtin.unarchive`
    Parameters: `src`, `dest`, `remote_src(bool)`, `creates`

**Need to manage services?**
├── systemd: `ansible.builtin.systemd_service` (note: NOT `ansible.builtin.systemd` in newer Ansible)
│   Parameters: `name`, `state(started/stopped/restarted/reloaded)`, `enabled`, `daemon_reload`
├── generic: `ansible.builtin.service`
│   Parameters: `name`, `state`, `enabled`
└── System reboot: `ansible.builtin.reboot`
    Parameters: `reboot_timeout`, `pre_reboot_delay`, `msg`

**Need to manage users/groups?**
├── User: `ansible.builtin.user`
│   Parameters: `name`, `state`, `uid`, `group`, `groups`, `append`, `shell`, `home`, `create_home`, `password`, `system`
├── Group: `ansible.builtin.group`
│   Parameters: `name`, `state`, `gid`, `system`
└── SSH key: `ansible.posix.authorized_key`
    Parameters: `user`, `key`, `state`, `exclusive`

**Need to run commands?**
├── Simple command (no shell features): `ansible.builtin.command`
│   Parameters: `cmd`, `chdir`, `creates`, `removes`
│   MUST ADD: `changed_when`
├── Shell features needed (pipes, redirects): `ansible.builtin.shell`
│   Parameters: `cmd`, `chdir`, `creates`, `removes`, `executable`
│   MUST ADD: `changed_when`
├── Raw SSH command (no Python needed): `ansible.builtin.raw`
│   Use ONLY for bootstrapping Python on target
└── Run local script on remote: `ansible.builtin.script`
    Parameters: `cmd`, `chdir`, `creates`, `removes`

**Need to handle data?**
├── Set variable: `ansible.builtin.set_fact`
│   Parameters: `key_name: value`, `cacheable(bool)`
├── Include variables: `ansible.builtin.include_vars`
│   Parameters: `file`, `dir`, `name`, `depth`
├── Debug/print: `ansible.builtin.debug`
│   Parameters: `msg`, `var`, `verbosity`
├── Register output: `register: result_var`
├── Pause: `ansible.builtin.pause`
│   Parameters: `seconds`, `minutes`, `prompt`
└── Fail: `ansible.builtin.fail`
    Parameters: `msg`, `when`

**Need to wait for something?**
├── Port/file: `ansible.builtin.wait_for`
│   Parameters: `host`, `port`, `path`, `state`, `timeout`, `delay`
└── SSH connection: `ansible.builtin.wait_for_connection`
    Parameters: `timeout`, `delay`, `sleep`

**Need to delegate?**
├── Run on specific host: `delegate_to: hostname`
├── Run locally: `delegate_to: localhost`
│   OR: `connection: local`
└── Run once across group: `run_once: true`

## Modules That DO NOT Exist (Common AI Inventions)

AI models often hallucinate module names or namespaces. Do NOT use these:

- `ansible.builtin.docker_container` → WRONG, use `community.docker.docker_container`
- `ansible.builtin.mysql_db` → WRONG, use `community.mysql.mysql_db`
- `ansible.builtin.postgresql_db` → WRONG, use `community.postgresql.postgresql_db`
- `ansible.builtin.firewalld` → WRONG, use `ansible.posix.firewalld`
- `ansible.builtin.seboolean` → WRONG, use `ansible.posix.seboolean`
- `ansible.builtin.authorized_key` → WRONG, use `ansible.posix.authorized_key`
- `ansible.builtin.mount` → Actually EXISTS (this is correct)
- `ansible.builtin.cron` → Actually EXISTS (this is correct)
- `ansible.builtin.at` → Actually EXISTS (this is correct)
- `ansible.builtin.k8s` → WRONG, use `kubernetes.core.k8s`
- `ansible.builtin.helm` → WRONG, use `kubernetes.core.helm`
- `ansible.builtin.aws_*` → WRONG, use `amazon.aws.*`
- `ansible.builtin.azure_*` → WRONG, use `azure.azcollection.*`
- `ansible.builtin.gcp_*` → WRONG, use `google.cloud.*`
- Any module starting with `ansible.community.*` → WRONG namespace, it's `community.*`

## Common Error Patterns and Fixes

```yaml
# ERROR 1: Using {{ }} in when clause
# BAD:
  when: "{{ my_var == 'value' }}"
# GOOD:
  when: my_var == 'value'

# ERROR 2: Missing quotes around mode
# BAD:
  mode: 0644
# GOOD:
  mode: '0644'

# ERROR 3: Using with_items instead of loop
# BAD:
  with_items: "{{ packages }}"
# GOOD:
  loop: "{{ packages }}"

# ERROR 4: Bare variable in task parameter
# BAD:
  src: my_template.j2
# GOOD (if it's a variable):
  src: "{{ my_template }}"
# GOOD (if it's a literal):
  src: my_template.j2

# ERROR 5: Not handling command state changes
# BAD:
- name: Run a command
  ansible.builtin.command: /opt/script.sh
# GOOD:
- name: Run a command
  ansible.builtin.command: /opt/script.sh
  changed_when: false # or a real condition

# ERROR 6: Using shell when not needed
# BAD:
- name: Remove file
  ansible.builtin.shell: rm -rf /tmp/foo
# GOOD:
- name: Remove file
  ansible.builtin.file:
    path: /tmp/foo
    state: absent

# ERROR 7: Missing become for root operations
# BAD:
- name: Install nginx
  ansible.builtin.apt:
    name: nginx
    state: present
# GOOD:
- name: Install nginx
  ansible.builtin.apt:
    name: nginx
    state: present
  become: true

# ERROR 8: Unquoted booleans
# BAD:
  backup: True
# GOOD:
  backup: true

# ERROR 9: Using old dictionary syntax
# BAD:
  ansible.builtin.user:
    name=jdoe state=present
# GOOD:
  ansible.builtin.user:
    name: jdoe
    state: present

# ERROR 10: Improper block/rescue nesting
# BAD:
  block:
    - task1
  rescue: task2
# GOOD:
  block:
    - name: task1
      ansible.builtin.debug: msg="task1"
  rescue:
    - name: task2
      ansible.builtin.debug: msg="task2"
```

## Mandatory Validation Steps

These MUST be completed before reporting your work as done:
1. `ansible-playbook --syntax-check <playbook>`
2. `ansible-lint <playbook>`
3. `./scripts/check-fqcn.sh` (if available in the repo)
4. Manually verify every module FQCN exists in `requirements.yml` collections
5. Fix ALL errors before proceeding.
