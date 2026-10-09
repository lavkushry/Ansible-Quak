---
name: ansible-akamai
description: >
  MANDATORY skill for automating Akamai EdgeGrid CDN, Edge DNS, Fast Purge (CCU v3),
  and Property Manager (PAPI). Enforces FQCN, accurate parameters, secure authentication,
  and anti-hallucination patterns.
---

# Akamai Automation Skill (`akamai.edgegrid`)

## Core Rule: Always Use `akamai.edgegrid` FQCN

Akamai modules belong exclusively to the `akamai.edgegrid` collection. NEVER use bare module names or invented `ansible.builtin.akamai_*` namespaces.

### Collection Installation
```yaml
# In requirements.yml
collections:
  - name: akamai.edgegrid
    version: ">=2.1.0"
```

---

## 1. Authentication Best Practices

Akamai API requests require OPEN EdgeGrid authentication credentials:
- `host` (Akamai API base URL, e.g., `akab-xxxx.luna.akamaiapis.com`)
- `client_token`
- `client_secret`
- `access_token`

### Pattern A: Using `edgerc` File (Recommended for Local/Tower Execution)
Store credentials in `~/.edgerc` (secured with `0600` permissions) and reference the section:
```yaml
- name: Purge Akamai cache using edgerc
  akamai.edgegrid.cache_purge:
    edgerc: "{{ ansible_env.HOME }}/.edgerc"
    section: "default"
    network: "production"
    objects:
      - "https://www.example.com/static/style.css"
      - "https://www.example.com/images/logo.png"
  delegate_to: localhost
  tags: ['akamai', 'purge']
```

### Pattern B: Passing Vault-Encrypted Credentials Directly
```yaml
- name: Fast Purge by CP Code using Vault variables
  akamai.edgegrid.cache_purge:
    hostname: "{{ vault_akamai_host }}"
    client_token: "{{ vault_akamai_client_token }}"
    client_secret: "{{ vault_akamai_client_secret }}"
    access_token: "{{ vault_akamai_access_token }}"
    network: "production"
    purge_type: "cpcode"
    action: "invalidate"
    objects:
      - "123456"
  delegate_to: localhost
  no_log: true
  tags: ['akamai', 'purge']
```

---

## 2. Fast Purge / Content Control Utility (CCU v3)

### Purge Types:
- `invalidate`: Marks content stale. Next user request gets updated content while origin serves stale if origin is slow (Safe, recommended).
- `delete`: Evicts content completely from Akamai edge caches (Forces origin refetch immediately).

### Common Tasks:

#### Invalidate URLs
```yaml
- name: Invalidate cache for updated frontend assets
  akamai.edgegrid.cache_purge:
    edgerc: "{{ akamai_edgerc_file }}"
    section: "{{ akamai_section | default('default') }}"
    network: "{{ akamai_network | default('production') }}"  # staging or production
    purge_type: "url"
    action: "invalidate"
    objects:
      - "https://{{ site_domain }}/app.js"
      - "https://{{ site_domain }}/main.css"
  delegate_to: localhost
  register: purge_result
  tags: ['akamai', 'purge']
```

#### Delete Cache by Cache Tags (Cache-Tag Purge)
```yaml
- name: Purge Akamai content by Cache-Tag
  akamai.edgegrid.cache_purge:
    edgerc: "{{ akamai_edgerc_file }}"
    section: "{{ akamai_section | default('default') }}"
    network: "production"
    purge_type: "tag"
    action: "delete"
    objects:
      - "product-catalog-2026"
  delegate_to: localhost
  tags: ['akamai', 'purge']
```

---

## 3. Akamai Edge DNS Automation

### Manage DNS Records (A, CNAME, TXT, MX)
```yaml
- name: Ensure DNS CNAME record points to Akamai Edge hostname
  akamai.edgegrid.dns_record:
    edgerc: "{{ akamai_edgerc_file }}"
    section: "{{ akamai_section }}"
    zone: "example.com"
    name: "api.example.com"
    type: "CNAME"
    target: ["api.example.com.edgekey.net."]
    ttl: 300
    active: true
    state: present
  delegate_to: localhost
  tags: ['akamai', 'dns']

- name: Create or update TXT record for domain validation
  akamai.edgegrid.dns_record:
    edgerc: "{{ akamai_edgerc_file }}"
    section: "{{ akamai_section }}"
    zone: "example.com"
    name: "_acme-challenge.example.com"
    type: "TXT"
    target: ['"k9s8d7f6a5b4c3d2e1"']
    ttl: 60
    state: present
  delegate_to: localhost
  tags: ['akamai', 'dns', 'acme']
```

---

## 4. Property Manager (PAPI) Automation

Manage Akamai Configurations (Delivery properties):
```yaml
- name: Activate Akamai Property on Staging network
  akamai.edgegrid.property_activation:
    edgerc: "{{ akamai_edgerc_file }}"
    section: "{{ akamai_section }}"
    property_name: "www.example.com"
    version: "{{ property_version }}"
    network: "STAGING"
    note: "Automated activation via Ansible pipeline #{{ build_number }}"
    notify_emails:
      - "devops-alerts@example.com"
  delegate_to: localhost
  register: papi_activation
  tags: ['akamai', 'papi']
```

---

## 5. Anti-Hallucination: Do NOT Invent These Modules

| Hallucinated / Deprecated Module | Correct Real FQCN |
|---|---|
| ❌ `akamai_purge` | ✅ `akamai.edgegrid.cache_purge` |
| ❌ `ansible.builtin.akamai_purge` | ✅ `akamai.edgegrid.cache_purge` |
| ❌ `akamai_dns` | ✅ `akamai.edgegrid.dns_record` |
| ❌ `akamai_papi` | ✅ `akamai.edgegrid.property_activation` |
| ❌ `akamai_fast_purge` | ✅ `akamai.edgegrid.cache_purge` with `purge_type` |
| ❌ `community.general.akamai` | ✅ `akamai.edgegrid.*` |

---

## 6. Pre-Execution Checklist
- [ ] Run from localhost (`delegate_to: localhost`) or dedicated automation runner.
- [ ] Always mask Akamai API secret keys using `no_log: true` when passing credentials in task parameters.
- [ ] Staging first: Always test Fast Purge or Property Activation against `STAGING` / `staging` before `PRODUCTION` / `production`.
- [ ] Trailing dot on DNS targets: CNAME and MX target values usually require a trailing dot (e.g. `edgekey.net.`).
