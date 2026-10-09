---
name: ansible-security-hardening
description: >
  Use when implementing security hardening, CIS benchmarks, compliance scanning,
  SSH hardening, firewall rules, SELinux/AppArmor, password policies, or audit logging.
---

# Ansible Security Hardening Skill

This skill outlines mandatory pre-steps, complete module parameter references, common error patterns, and battle-tested examples for enterprise security hardening automation.

## Mandatory Pre-Steps
1. Understand the target OS and its default security mechanisms (e.g., SELinux for RHEL/CentOS, AppArmor for Debian/Ubuntu).
2. Review the organizational security policies or compliance frameworks (e.g., CIS benchmarks, DISA STIG).
3. Do not blindly apply hardening rules without testing; some changes (like strict SSH settings or aggressive firewall rules) can lock you out of the server.

## 1. SSH Hardening

Always deploy a secured `sshd_config` file and restart the SSH service. Use the `validate` parameter to ensure the configuration syntax is correct before applying.

```yaml
- name: Deploy hardened sshd configuration
  ansible.builtin.template:
    src: sshd_config.j2
    dest: /etc/ssh/sshd_config
    owner: root
    group: root
    mode: '0600'
    validate: 'sshd -t -f %s'
  notify: Restart sshd
  become: true
  tags: ['security', 'ssh', 'hardening']
```

### Essential `sshd_config` Settings
Ensure the template (`sshd_config.j2`) includes the following:
```sshdconfig
# Authentication
PermitRootLogin no
PasswordAuthentication no
PermitEmptyPasswords no
MaxAuthTries 3

# Session Management
ClientAliveInterval 300
ClientAliveCountMax 0

# Network
Protocol 2
ListenAddress 0.0.0.0
# Add AllowUsers or AllowGroups if needed

# Crypto
KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,umac-128-etm@openssh.com
```

## 2. Firewall Hardening Patterns

### UFW (Ubuntu/Debian)
```yaml
- name: Set UFW default deny outgoing, deny incoming
  community.general.ufw:
    direction: "{{ item.dir }}"
    policy: deny
  loop:
    - { dir: 'incoming' }
    - { dir: 'outgoing' }
    - { dir: 'routed' }
  become: true
  tags: ['security', 'firewall']

- name: Allow essential outgoing traffic
  community.general.ufw:
    rule: allow
    direction: outgoing
    port: "{{ item }}"
  loop: ['53', '80', '443', '123']
  become: true

- name: Limit SSH to prevent brute force
  community.general.ufw:
    rule: limit
    port: '22'
    proto: tcp
  become: true
```

### Firewalld (RHEL/CentOS)
```yaml
- name: Configure firewalld rules
  ansible.posix.firewalld:
    service: "{{ item }}"
    permanent: true
    state: enabled
    immediate: true
  loop:
    - ssh
    - http
    - https
  become: true
```

## 3. User & Password Security

### Password Complexity (PAM)
```yaml
- name: Configure PAM password quality (RHEL-based)
  ansible.builtin.lineinfile:
    path: /etc/security/pwquality.conf
    regexp: "^{{ item.key }}"
    line: "{{ item.key }} = {{ item.value }}"
    state: present
  loop:
    - { key: 'minlen', value: '14' }
    - { key: 'dcredit', value: '-1' }
    - { key: 'ucredit', value: '-1' }
    - { key: 'ocredit', value: '-1' }
    - { key: 'lcredit', value: '-1' }
  become: true
```

### Remove Unnecessary Users
```yaml
- name: Remove unused default users
  ansible.builtin.user:
    name: "{{ item }}"
    state: absent
    remove: true
  loop:
    - games
    - ftp
  become: true
```

## 4. File System Security

### Mount Options
```yaml
- name: Ensure /tmp is mounted with secure options
  ansible.posix.mount:
    path: /tmp
    src: tmpfs
    fstype: tmpfs
    opts: nodev,nosuid,noexec
    state: mounted
  become: true
```

### File Permissions
```yaml
- name: Set secure permissions on shadow file
  ansible.builtin.file:
    path: /etc/shadow
    owner: root
    group: shadow
    mode: '0640'
  become: true
```

## 5. Kernel Hardening (sysctl)

```yaml
- name: Apply kernel hardening parameters
  ansible.posix.sysctl:
    name: "{{ item.key }}"
    value: "{{ item.value }}"
    sysctl_set: true
    state: present
    reload: true
  loop:
    - { key: 'net.ipv4.ip_forward', value: '0' }
    - { key: 'net.ipv4.conf.all.send_redirects', value: '0' }
    - { key: 'net.ipv4.conf.all.accept_redirects', value: '0' }
    - { key: 'net.ipv4.conf.all.accept_source_route', value: '0' }
    - { key: 'net.ipv4.conf.all.log_martians', value: '1' }
    - { key: 'net.ipv4.icmp_echo_ignore_broadcasts', value: '1' }
    - { key: 'kernel.randomize_va_space', value: '2' }
    - { key: 'fs.suid_dumpable', value: '0' }
  become: true
  tags: ['security', 'kernel']
```

## 6. Audit Logging (Auditd)

```yaml
- name: Ensure auditd is installed and enabled
  ansible.builtin.package:
    name: auditd
    state: present
  become: true

- name: Enable auditd service
  ansible.builtin.service:
    name: auditd
    state: started
    enabled: true
  become: true
```

## 7. SELinux Management

Always prefer `ansible.posix.selinux` and `ansible.posix.seboolean` for managing SELinux state.

```yaml
- name: Ensure SELinux is enforcing
  ansible.posix.selinux:
    policy: targeted
    state: enforcing
  become: true

- name: Set HTTPD network connect boolean
  ansible.posix.seboolean:
    name: httpd_can_network_connect
    state: true
    persistent: true
  become: true
```

## 8. Anti-Hallucination & Error Patterns
- `sysctl` module belongs to `ansible.posix` collection (`ansible.posix.sysctl`).
- `firewalld` module belongs to `ansible.posix` collection (`ansible.posix.firewalld`).
- `ufw` module belongs to `community.general` collection (`community.general.ufw`).
- `mount` module belongs to `ansible.posix` collection (`ansible.posix.mount`).
- Never run a simple command `iptables` via `ansible.builtin.shell`, always use a dedicated firewall module or the `ansible.builtin.iptables` module.
