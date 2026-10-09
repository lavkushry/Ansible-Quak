---
name: ansible-linux-admin
description: >
  Use for daily Linux server administration tasks: package management, user management,
  service management, firewall configuration, filesystem operations, cron jobs,
  system hardening, and monitoring setup.
---

# Ansible Linux Administration Guide

This guide provides reliable, idempotent task patterns for common Linux administration.

## 1. Package Management

**Install Packages (Cross-platform)**
```yaml
- name: Install essential packages
  ansible.builtin.package:
    name:
      - curl
      - git
      - htop
    state: present
  become: true
```

**Install Packages (Debian/Ubuntu Specific with apt cache update)**
```yaml
- name: Install nginx on Debian
  ansible.builtin.apt:
    name: nginx
    state: present
    update_cache: true
    cache_valid_time: 3600
  become: true
```

**Pin Package Versions (RHEL/CentOS)**
```yaml
- name: Install specific version of docker-ce
  ansible.builtin.dnf:
    name: docker-ce-24.0.5
    state: present
    allow_downgrade: true
  become: true
```

## 2. User & Group Management

**Create Service Account**
```yaml
- name: Create prometheus system user
  ansible.builtin.user:
    name: prometheus
    system: true
    shell: /sbin/nologin
    create_home: false
    state: present
  become: true
```

**Create Admin User with SSH Key**
```yaml
- name: Create admin user
  ansible.builtin.user:
    name: admin
    groups: wheel,docker
    append: true
    shell: /bin/bash
    create_home: true
  become: true

- name: Deploy SSH key for admin
  ansible.posix.authorized_key:
    user: admin
    state: present
    key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... admin@local"
  become: true
```

**Sudoers Configuration (Safest Method)**
```yaml
- name: Allow wheel group to have passwordless sudo
  ansible.builtin.copy:
    content: "%wheel ALL=(ALL) NOPASSWD: ALL"
    dest: /etc/sudoers.d/wheel_nopasswd
    mode: '0440'
    validate: /usr/sbin/visudo -cf %s
  become: true
```
*Never edit `/etc/sudoers` directly with lineinfile or template without validation!*

## 3. Service Management

**Systemd Service Management**
```yaml
- name: Ensure nginx is started and enabled at boot
  ansible.builtin.systemd_service:
    name: nginx
    state: started
    enabled: true
    daemon_reload: true
  become: true
```

## 4. Firewall Configuration

**UFW (Ubuntu/Debian)**
```yaml
- name: Allow SSH, HTTP, HTTPS in UFW
  community.general.ufw:
    rule: allow
    port: "{{ item }}"
    proto: tcp
  loop:
    - '22'
    - '80'
    - '443'
  become: true

- name: Enable UFW
  community.general.ufw:
    state: enabled
    policy: deny
  become: true
```

**Firewalld (RHEL/CentOS)**
```yaml
- name: Allow HTTP in firewalld
  ansible.posix.firewalld:
    service: http
    permanent: true
    state: enabled
    immediate: true
  become: true
```

## 5. Filesystem Operations

**Directory Creation and Permissions**
```yaml
- name: Ensure app directory exists with correct permissions
  ansible.builtin.file:
    path: /opt/myapp/data
    state: directory
    owner: appuser
    group: appgroup
    mode: '0750'
  become: true
```

**Mounting Filesystems**
```yaml
- name: Mount extra disk
  ansible.posix.mount:
    path: /data
    src: /dev/sdb1
    fstype: ext4
    opts: defaults
    state: mounted
  become: true
```

## 6. Cron & Scheduled Tasks

**Standard Cron Job**
```yaml
- name: Run backup script daily at 2am
  ansible.builtin.cron:
    name: "Daily database backup"
    minute: "0"
    hour: "2"
    job: "/usr/local/bin/backup.sh > /dev/null 2>&1"
    user: dbadmin
  become: true
```

## 7. System Configuration

**Hostname Configuration**
```yaml
- name: Set hostname
  ansible.builtin.hostname:
    name: web-prod-01
  become: true
```

**Sysctl Parameter Tuning**
```yaml
- name: Optimize network settings
  ansible.posix.sysctl:
    name: net.ipv4.ip_forward
    value: '1'
    sysctl_set: true
    state: present
    reload: true
  become: true
```

## 8. Monitoring & Logging

**Log Rotation Configuration**
```yaml
- name: Configure log rotation for custom app
  ansible.builtin.copy:
    dest: /etc/logrotate.d/myapp
    content: |
      /var/log/myapp/*.log {
          daily
          missingok
          rotate 14
          compress
          delaycompress
          notifempty
          create 0640 appuser appgroup
      }
    mode: '0644'
  become: true
```
