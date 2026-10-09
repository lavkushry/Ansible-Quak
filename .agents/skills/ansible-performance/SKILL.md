---
name: ansible-performance
description: >
  Use when optimizing Ansible playbook execution speed, managing large inventories,
  using async tasks, configuring strategies, and tuning for production scale.
---

# Ansible Performance and Optimization Guide

When dealing with large inventories or slow operations, Ansible provides several native ways to optimize execution speed.

## 1. Execution Strategies

The way Ansible dispatches tasks to hosts is controlled by strategies:

- **linear** (default): One task at a time across all hosts. Host A and Host B must both finish Task 1 before either can move to Task 2.
- **free**: Each host runs tasks as fast as it can independently. Host A can finish the playbook while Host B is still on Task 1. Best for independent server bootstrapping.
- **host_pinned**: Similar to free, but limits the number of active hosts (based on forks). Once a host starts, it completes all tasks before a new host is scheduled.

**How to set it:**
```yaml
- name: Bootstrap servers quickly
  hosts: webservers
  strategy: free
  tasks:
    # ...
```

## 2. Fact Gathering Optimization

Gathering facts takes time (often 1-3 seconds per host).

- **Disable if not needed:**
  ```yaml
  - name: Simple updates
    hosts: all
    gather_facts: false
  ```

- **Limit gathered facts:**
  ```yaml
  - name: Limited facts
    hosts: all
    gather_subset:
      - '!all'
      - 'network'
  ```

- **Fact Caching (`ansible.cfg`):**
  ```ini
  [defaults]
  gathering = smart
  fact_caching = jsonfile
  fact_caching_connection = /tmp/ansible_fact_cache
  fact_caching_timeout = 86400
  ```

## 3. Async Tasks

For long-running tasks, don't keep the SSH connection open waiting for it to finish.

**Complete Syntax:**
```yaml
- name: Long running database migration
  ansible.builtin.command: /opt/run-migration.sh
  async: 3600      # Max time to wait in seconds
  poll: 0          # Return immediately, don't wait
  register: migration_job

- name: Do other quick things while migration runs
  ansible.builtin.debug:
    msg: "Doing work in parallel..."

- name: Check on migration status
  ansible.builtin.async_status:
    jid: "{{ migration_job.ansible_job_id }}"
  register: job_result
  until: job_result.finished
  retries: 60      # How many times to check
  delay: 30        # Seconds between checks
```

## 4. Connection Optimization

Tune your `ansible.cfg` for SSH connection speedups.

```ini
[defaults]
# Increase number of concurrent parallel processes (default is 5)
forks = 50

[ssh_connection]
# Pipelining reduces the number of SSH operations required to execute a module
# Requires `requiretty` to be disabled in /etc/sudoers on target machines
pipelining = True

# ControlMaster settings reuse SSH connections
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

*Note: Mitogen is an alternative connection plugin that can speed up runs by 2-7x, but requires separate installation.*

## 5. Task-Level Optimization

- **`serial` (Rolling Updates):**
  Update web servers 2 at a time to prevent downtime.
  ```yaml
  - hosts: webservers
    serial: 2
    tasks: ...
  ```

- **`throttle`:**
  Limit concurrency for a specific task (e.g., calling an API with rate limits).
  ```yaml
  - name: Call API
    ansible.builtin.uri:
      url: "https://api.example.com/update"
    throttle: 1
  ```

- **`run_once`:**
  Execute a task exactly once across the whole play, regardless of how many hosts are matched.
  ```yaml
  - name: Notify Slack of deployment start
    community.general.slack:
      msg: "Starting deployment to {{ ansible_play_batch | length }} hosts"
    run_once: true
    delegate_to: localhost
  ```

- **Avoid shell/command loops!**
  Spawning an SSH connection and a shell process for each item in a loop is extremely slow.
  ```yaml
  # BAD - Slow
  - name: Install packages
    ansible.builtin.command: yum install -y {{ item }}
    loop: "{{ package_list }}"

  # GOOD - Fast (Module handles the list in one operation)
  - name: Install packages
    ansible.builtin.dnf:
      name: "{{ package_list }}"
      state: present
  ```

## 6. Large Inventory Tips

- **Dynamic Inventory Caching:** If using AWS/GCP dynamic inventory, cache it so you don't hit cloud APIs every run.
- **Limit runs:** Always test with `--limit host1,host2` before running on 1000 nodes.
- **Tags:** Use tags extensively so you can run only the specific parts of a playbook you need (`--tags "nginx,ssl"`).
- **Include vs Import:**
  - `import_tasks` is static and parsed at playbook load time. (Better for performance, fewer loop options).
  - `include_tasks` is dynamic and parsed at runtime. (More flexible, slightly slower).
