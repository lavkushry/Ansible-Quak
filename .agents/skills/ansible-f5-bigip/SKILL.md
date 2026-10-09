---
name: ansible-f5-bigip
description: >
  MANDATORY skill for automating F5 BIG-IP Application Delivery Controllers (ADC),
  AS3 declarative deployments, pool member maintenance drain, virtual servers,
  nodes, and SSL profiles using f5networks.f5_modules.
---

# F5 BIG-IP Automation Skill (`f5networks.f5_modules`)

## Core Rule: Always Use `f5networks.f5_modules` FQCN

F5 modules are maintained under the `f5networks.f5_modules` collection. NEVER use bare module names like `bigip_pool` or `bigip_virtual_server`.

```yaml
# In requirements.yml
collections:
  - name: f5networks.f5_modules
    version: ">=1.29.0"
```

---

## 1. Authentication & Provider Dictionary

Every F5 task communicates via iControl REST. Always define the `provider` dictionary or pass it via inventory/group variables:

```yaml
# In group_vars/f5_appliances.yml
f5_provider:
  server: "{{ inventory_hostname }}"
  user: "{{ vault_f5_username }}"
  password: "{{ vault_f5_password }}"
  server_port: 443
  validate_certs: false  # Set to true in strict production PKI environments
  transport: rest
```

Then pass `provider: "{{ f5_provider }}"` to each task, running on `delegate_to: localhost`.

---

## 2. Declarative AS3 Deployments (Recommended Architecture)

F5 Application Services 3 (AS3) is the gold standard for Declarative, idempotent L4-L7 application deployments.

```yaml
- name: Deploy HTTP/HTTPS Application via F5 AS3 Declaration
  f5networks.f5_modules.bigip_as3_deploy:
    provider: "{{ f5_provider }}"
    content: "{{ lookup('ansible.builtin.template', 'as3_app_declaration.json.j2') }}"
    tenant: "Sample_Tenant"
  delegate_to: localhost
  tags: ['f5', 'as3']
```

### AS3 Declaration Jinja2 Template (`templates/as3_app_declaration.json.j2`)
```json
{
  "$schema": "https://raw.githubusercontent.com/F5Networks/f5-appsvcs-extension/master/schema/latest/as3-schema.json",
  "class": "AS3",
  "action": "deploy",
  "persist": true,
  "declaration": {
    "class": "ADC",
    "schemaVersion": "3.45.0",
    "id": "app_deployment_{{ env_name }}",
    "Sample_Tenant": {
      "class": "Tenant",
      "Web_App": {
        "class": "Application",
        "template": "http",
        "serviceMain": {
          "class": "Service_HTTP",
          "virtualAddresses": ["{{ app_vip_ip }}"],
          "virtualPort": 80,
          "pool": "web_pool"
        },
        "web_pool": {
          "class": "Pool",
          "monitors": ["http"],
          "members": [
            {% for host in groups['webservers'] %}
            {
              "servicePort": 8080,
              "serverAddresses": ["{{ hostvars[host]['ansible_host'] }}"]
            }{{ "," if not loop.last else "" }}
            {% endfor %}
          ]
        }
      }
    }
  }
}
```

---

## 3. Imperative Task Patterns (L4-L7 Objects)

### Pattern 1: Manage Backend Nodes
```yaml
- name: Ensure backend node exists
  f5networks.f5_modules.bigip_node:
    provider: "{{ f5_provider }}"
    name: "web-app-01.corp.internal"
    host: "10.100.20.11"
    state: present
    partition: "Common"
  delegate_to: localhost
  tags: ['f5', 'node']
```

### Pattern 2: Manage Pool & Health Monitor
```yaml
- name: Create Load Balancing Pool with HTTP Monitor
  f5networks.f5_modules.bigip_pool:
    provider: "{{ f5_provider }}"
    name: "app_http_pool"
    lb_method: "round-robin"
    monitors:
      - "/Common/http"
    partition: "Common"
    state: present
  delegate_to: localhost
  tags: ['f5', 'pool']
```

### Pattern 3: Maintenance Window — Graceful Member Drain
When performing rolling OS upgrades or app updates, gracefully drain members before taking them down:

```yaml
# Step 1: Drain active connections (new sessions go to other members)
- name: Disable pool member for maintenance (Drain mode)
  f5networks.f5_modules.bigip_pool_member:
    provider: "{{ f5_provider }}"
    pool: "app_http_pool"
    partition: "Common"
    name: "{{ inventory_hostname }}:8080"
    state: "disabled"       # user-disabled: finishes existing sessions
    # state: "forced_offline"  # hard-drop: cuts all existing connections
  delegate_to: localhost
  tags: ['f5', 'drain']

# Step 2: Post-maintenance re-enable
- name: Re-enable pool member after maintenance
  f5networks.f5_modules.bigip_pool_member:
    provider: "{{ f5_provider }}"
    pool: "app_http_pool"
    partition: "Common"
    name: "{{ inventory_hostname }}:8080"
    state: "enabled"
  delegate_to: localhost
  tags: ['f5', 'enable']
```

### Pattern 4: Create Virtual Server (VIP)
```yaml
- name: Ensure HTTPS Virtual Server is configured
  f5networks.f5_modules.bigip_virtual_server:
    provider: "{{ f5_provider }}"
    name: "vs_app_https"
    destination: "10.100.20.50"
    port: 443
    pool: "app_http_pool"
    profiles:
      - "/Common/tcp"
      - "/Common/http"
      - "/Common/app_client_ssl_profile"
    snat: "Automap"
    state: present
    partition: "Common"
  delegate_to: localhost
  tags: ['f5', 'vip']
```

### Pattern 5: SSL Certificate and Key Renewal
```yaml
- name: Upload new SSL Certificate to F5
  f5networks.f5_modules.bigip_ssl_certificate:
    provider: "{{ f5_provider }}"
    name: "wildcard_cert_2026"
    content: "{{ lookup('ansible.builtin.file', 'certs/wildcard_2026.crt') }}"
    partition: "Common"
    state: present
  delegate_to: localhost
  tags: ['f5', 'ssl']

- name: Upload corresponding SSL Private Key
  f5networks.f5_modules.bigip_ssl_key:
    provider: "{{ f5_provider }}"
    name: "wildcard_key_2026"
    content: "{{ vault_wildcard_ssl_private_key }}"
    partition: "Common"
    state: present
  delegate_to: localhost
  no_log: true
  tags: ['f5', 'ssl']
```

---

## 4. Anti-Hallucination: Module Names & Options

| Hallucinated / Incorrect Syntax | Correct FQCN / Option |
|---|---|
| ❌ `bigip_pool` | ✅ `f5networks.f5_modules.bigip_pool` |
| ❌ `bigip_virtual_server` | ✅ `f5networks.f5_modules.bigip_virtual_server` |
| ❌ `ansible.builtin.bigip_*` | ✅ `f5networks.f5_modules.bigip_*` |
| ❌ `state: offline` | ✅ `state: forced_offline` or `state: disabled` |
| ❌ `server_ip: "1.2.3.4"` in provider | ✅ `server: "1.2.3.4"` |
| ❌ `host: "{{ f5_ip }}"` in task | ✅ Put in `provider:` dictionary |
| ❌ `bigip_as3` | ✅ `f5networks.f5_modules.bigip_as3_deploy` |

---

## 5. Pre-Flight Checklist
- [ ] Always execute against F5 via `delegate_to: localhost`.
- [ ] Provider dictionary credentials must come from Ansible Vault with `no_log: true`.
- [ ] When using AS3, validate JSON schema before deployment.
- [ ] In HA pairs, configure sync or target the active device (`bigip_configsync_action`).
