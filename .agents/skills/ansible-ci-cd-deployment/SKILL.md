---
name: ansible-ci-cd-deployment
description: >
  Use when writing playbooks for application deployments, rolling updates,
  blue-green deployments, canary releases, or CI/CD pipeline integration.
---

# Ansible CI/CD & Deployment Patterns Deep-Dive

## Mandatory Pre-Steps
1. Decide the deployment strategy: Big Bang, Rolling, Blue/Green, or Canary.
2. NEVER deploy without health checks built into the playbook.
3. Understand Ansible's execution strategy (`linear` vs `free`) and the `serial` keyword.

---

## 1. Rolling Update Pattern (Zero Downtime)

Updates servers in batches. The load balancer is updated to drain traffic, the app is updated, tested, and re-added to the load balancer.

```yaml
- name: Rolling Deployment for Web Applications
  hosts: webservers
  # Deploy to 25% of the fleet at a time
  serial: "25%"
  # Halt the entire playbook if 10% of hosts fail
  max_fail_percentage: 10
  # Avoid updating all hosts in one AZ at the same time
  order: shuffle

  pre_tasks:
    - name: Remove node from load balancer (Example HAProxy/F5/AWS ALB)
      ansible.builtin.command: "/opt/lb/drain.sh {{ inventory_hostname }}"
      delegate_to: loadbalancer_host

  roles:
    - role: deploy_application
      vars:
        app_version: "{{ lookup('env', 'DEPLOY_VERSION') }}"

  post_tasks:
    - name: Wait for application to come up
      ansible.builtin.wait_for:
        port: 8080
        delay: 5
        timeout: 60

    - name: Run local smoke tests / Healthcheck
      ansible.builtin.uri:
        url: "http://{{ ansible_host }}:8080/healthz"
        status_code: 200
        return_content: true
      register: healthcheck
      failed_when: "'OK' not in healthcheck.content"

    - name: Re-add node to load balancer
      ansible.builtin.command: "/opt/lb/enable.sh {{ inventory_hostname }}"
      delegate_to: loadbalancer_host
```

---

## 2. Canary Release Pattern

A variant of the rolling update, but you scale up the batches gradually.

```yaml
- name: Canary Deployment
  hosts: webservers
  # Update 1 host, then 10% of hosts, then the rest
  serial:
    - 1
    - "10%"
    - "100%"
```
This allows you to catch errors on a single host before destroying 10% or 100% of the fleet.

---

## 3. Database Migration Handling (`run_once`)

When deploying applications, DB schema migrations should only run exactly ONCE per deployment, not once per web server.

```yaml
- name: Run Database Migrations
  ansible.builtin.command: "flask db upgrade"
  args:
    chdir: "/opt/app"
  run_once: true
  delegate_to: "{{ groups['webservers'][0] }}"
  environment:
    DB_URL: "{{ vault_db_url }}"
```

---

## 4. Rollback Strategy using Block/Rescue

Automate rollbacks using Ansible's native error handling mechanism.

```yaml
- name: Safe Deployment Block
  block:
    - name: Deploy new application code
      ansible.builtin.unarchive:
        src: "app-{{ version }}.tar.gz"
        dest: /opt/app
    
    - name: Restart application service
      ansible.builtin.systemd:
        name: myapp
        state: restarted
        
    - name: Verify application is healthy
      ansible.builtin.uri:
        url: http://localhost/health
        status_code: 200

  rescue:
    - name: ALERT - Deployment Failed
      ansible.builtin.debug:
        msg: "Deployment failed! Initiating rollback."

    - name: Rollback to previous version
      ansible.builtin.command: "/opt/app/rollback.sh"
      
    - name: Restart application service (rollback)
      ansible.builtin.systemd:
        name: myapp
        state: restarted

    - name: Fail the playbook
      ansible.builtin.fail:
        msg: "Deployment failed and rolled back safely."
```

---

## 5. CI/CD Integration (GitHub Actions)

Example of pulling artifacts and deploying in an ephemeral CI runner:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Setup SSH Key
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan github.com >> ~/.ssh/known_hosts

      - name: Run Ansible Playbook
        env:
          ANSIBLE_HOST_KEY_CHECKING: "false"
        run: |
          ansible-playbook -i inventory/production playbook.yml \
            -e "app_version=${{ github.sha }}"
```

---

## 6. Notifications & ChatOps

Always notify the team upon success or failure.

```yaml
- name: Notify Slack of deployment success
  community.general.slack:
    token: "{{ vault_slack_token }}"
    channel: '#deployments'
    msg: "✅ Deployment of version {{ app_version }} to production completed successfully!"
  run_once: true
  delegate_to: localhost
```
