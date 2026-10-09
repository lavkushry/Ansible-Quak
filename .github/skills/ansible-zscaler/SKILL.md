---
name: ansible-zscaler
description: >
  MANDATORY skill for automating Zscaler Internet Access (ZIA) and Zscaler Private Access (ZPA)
  cloud security policies, application segments, server groups, and URL filtering.
---

# Zscaler Automation Skill (`zscaler.ziacloud` & `zscaler.zpacloud`)

## Core Rule: Differentiate ZIA vs ZPA Collections

Zscaler automation is divided into two distinct collections. NEVER mix their modules:
- **ZIA (Internet Access & Security)**: `zscaler.ziacloud.*`
- **ZPA (Private Access & Zero Trust App Access)**: `zscaler.zpacloud.*`

```yaml
# In requirements.yml
collections:
  - name: zscaler.ziacloud
    version: ">=1.0.0"
  - name: zscaler.zpacloud
    version: ">=1.0.0"
```

---

## 1. Authentication Configuration

### Authentication for ZIA (`zscaler.ziacloud`)
Requires API Key, Username, Password, and Cloud environment:
```yaml
# In group_vars/all/vault.yml
vault_zia_cloud: "zscaler.net"  # e.g., zscaler.net, zscalerone.net, zscalertwo.net
vault_zia_username: "admin@corp.com"
vault_zia_password: "supersecretpassword"
vault_zia_api_key: "api_key_string"
```

Can be passed to tasks or set as environment variables:
`ZIA_USERNAME`, `ZIA_PASSWORD`, `ZIA_API_KEY`, `ZIA_CLOUD`.

### Authentication for ZPA (`zscaler.zpacloud`)
Requires OAuth Client ID, Client Secret, and Customer ID:
```yaml
# Environment variables or task parameters:
# ZPA_CLIENT_ID, ZPA_CLIENT_SECRET, ZPA_CUSTOMER_ID, ZPA_CLOUD
vault_zpa_client_id: "oauth-client-id"
vault_zpa_client_secret: "oauth-client-secret"
vault_zpa_customer_id: "1234567890"
vault_zpa_cloud: "PRODUCTION"
```

---

## 2. Zscaler Internet Access (ZIA) Automation

### Manage Custom URL Categories (Whitelist / Blacklist)
```yaml
- name: Ensure Corporate URL Category contains approved partner domains
  zscaler.ziacloud.zia_url_categories:
    provider:
      username: "{{ vault_zia_username }}"
      password: "{{ vault_zia_password }}"
      api_key: "{{ vault_zia_api_key }}"
      cloud: "{{ vault_zia_cloud }}"
    configured_name: "Approved_Partner_APIs"
    super_category: "USER_DEFINED"
    urls:
      - "partner-api.vendor.com"
      - "secure-data.analytics.io"
      - ".cdn.partner-assets.net"
    state: present
  delegate_to: localhost
  no_log: true
  tags: ['zscaler', 'zia', 'url_categories']
```

### Manage URL Filtering Policy Rule
```yaml
- name: Allow traffic to Approved Partner APIs
  zscaler.ziacloud.zia_url_filtering_rules:
    provider:
      username: "{{ vault_zia_username }}"
      password: "{{ vault_zia_password }}"
      api_key: "{{ vault_zia_api_key }}"
      cloud: "{{ vault_zia_cloud }}"
    name: "Allow_Partner_Data_APIs"
    action: "ALLOW"
    order: 10
    state: "ENABLED"
    protocols:
      - "HTTPS_RULE"
      - "HTTP_RULE"
    url_categories:
      - "Approved_Partner_APIs"
    departments:
      - "Engineering"
      - "DataPlatform"
  delegate_to: localhost
  no_log: true
  tags: ['zscaler', 'zia', 'policy']
```

### Activate Changes in ZIA
```yaml
- name: Activate committed policy changes in ZIA
  zscaler.ziacloud.zia_activation_status:
    provider:
      username: "{{ vault_zia_username }}"
      password: "{{ vault_zia_password }}"
      api_key: "{{ vault_zia_api_key }}"
      cloud: "{{ vault_zia_cloud }}"
    status: "ACTIVE"
  delegate_to: localhost
  no_log: true
  tags: ['zscaler', 'zia', 'activate']
```

---

## 3. Zscaler Private Access (ZPA) Automation

### Manage Server Groups (Internal Workloads)
```yaml
- name: Ensure Server Group exists for Backend Database Cluster
  zscaler.zpacloud.zpa_server_group:
    client_id: "{{ vault_zpa_client_id }}"
    client_secret: "{{ vault_zpa_client_secret }}"
    customer_id: "{{ vault_zpa_customer_id }}"
    name: "Internal_Postgres_Cluster"
    description: "Managed via Ansible Pipeline"
    enabled: true
    dynamic_discovery: true
    app_connector_groups:
      - id: "{{ app_connector_group_id }}"
  delegate_to: localhost
  no_log: true
  tags: ['zscaler', 'zpa', 'server_group']
```

### Manage Application Segments (Zero Trust Access Definition)
```yaml
- name: Create or update ZPA Application Segment for Developer Access
  zscaler.zpacloud.zpa_application_segment:
    client_id: "{{ vault_zpa_client_id }}"
    client_secret: "{{ vault_zpa_client_secret }}"
    customer_id: "{{ vault_zpa_customer_id }}"
    name: "Grafana_Internal_Monitoring"
    description: "Internal Observability Dashboard"
    enabled: true
    domain_names:
      - "grafana.internal.corp"
      - "prometheus.internal.corp"
    segment_group_id: "{{ monitoring_segment_group_id }}"
    server_groups:
      - id: "{{ monitoring_server_group_id }}"
    tcp_port_ranges:
      - "3000"
      - "9090"
    is_cname_enabled: true
  delegate_to: localhost
  no_log: true
  tags: ['zscaler', 'zpa', 'app_segment']
```

---

## 4. Anti-Hallucination: Module Names & Cross-Collection Errors

| Hallucinated / Wrong Module | Correct Collection & Module |
|---|---|
| ❌ `zscaler_url_filter` | ✅ `zscaler.ziacloud.zia_url_filtering_rules` |
| ❌ `zscaler_app_segment` | ✅ `zscaler.zpacloud.zpa_application_segment` |
| ❌ `ansible.builtin.zscaler_*` | ✅ `zscaler.ziacloud.*` or `zscaler.zpacloud.*` |
| ❌ `zscaler.ziacloud.zpa_app_segment` | ✅ Wrong collection! Use `zscaler.zpacloud.zpa_application_segment` |
| ❌ `zscaler.zpacloud.zia_url_categories` | ✅ Wrong collection! Use `zscaler.ziacloud.zia_url_categories` |

---

## 5. Pre-Flight Checklist
- [ ] Always execute on `delegate_to: localhost`.
- [ ] OAuth token / API credentials must be secured in Vault and marked `no_log: true`.
- [ ] In ZIA, changes are staged until `zia_activation` is triggered. Include activation tasks.
- [ ] In ZPA, link Application Segments to real `segment_group_id` and `server_groups`.
