# GitHub Copilot Custom Instructions for Enterprise Ansible Automation

> CRITICAL: These rules are strictly enforced for all Ansible playbooks, roles, and tasks.
> Never guess modules or parameters. Follow every single rule below.

## 0. Anti-Overworking & Minimal Output Rules (NO BLOAT)
- **Do NOT Overwork or Over-Engineer**: If the user asks for a task, output ONLY that specific task (indented YAML). DO NOT generate an entire 50-line playbook, fictional inventories, roles, or variable files unless explicitly asked for a full playbook.
- **NO Unsolicited Boilerplate**: Do NOT add extra pre_tasks, post_tasks, handlers, backup steps, or debug messages unless specifically requested.
- **Minimal Required Parameters**: Only include parameters necessary for the requested action. Never dump 15 optional parameters into a task block.
- **Code First, Minimal Prose**: Put the YAML snippet immediately at the top of the response. Limit explanations to 1-2 bullet points maximum. No lengthy textbook introductions.
- **Strictly Grounded in Installed Collections**: Only output modules and parameters that exist in: `f5networks.f5_modules`, `akamai.edgegrid`, `zscaler.ziacloud`, `zscaler.zpacloud`, `community.general.jira`, `ansible.builtin`, `ansible.posix`.

## 1. Enterprise Module Rules (Anti-Hallucination & FQCN)

### FQCN is MANDATORY
- ALWAYS use Fully Qualified Collection Names (FQCN).
- ✅ `ansible.builtin.copy` | ❌ `copy`
- ✅ `akamai.edgegrid.cache_purge` | ❌ `akamai_purge`
- ✅ `f5networks.f5_modules.bigip_pool_member` | ❌ `bigip_pool_member`
- ✅ `zscaler.ziacloud.zia_url_categories` | ❌ `zscaler_url_category`
- ✅ `zscaler.zpacloud.zpa_application_segment` | ❌ `zpa_app_segment`
- ✅ `community.general.jira` | ❌ `jira` or `ansible.builtin.jira`
- ✅ `amazon.aws.ec2_instance` | ❌ `ec2`
- ✅ `azure.azcollection.azure_rm_virtualmachine` | ❌ `azure_rm_virtualmachine`
- ✅ `google.cloud.gcp_compute_instance` | ❌ `gce_instance`

### Enterprise Collection Boundaries
- **Akamai CDN & Edge DNS**: `akamai.edgegrid.*`
  - Purge: `akamai.edgegrid.cache_purge` (purge_type: url, cpcode, tag; action: invalidate, delete)
  - DNS: `akamai.edgegrid.dns_record`
  - Property Manager: `akamai.edgegrid.property_activation`
- **F5 BIG-IP ADC**: `f5networks.f5_modules.*`
  - Declarative AS3: `f5networks.f5_modules.bigip_as3_deploy`
  - Virtual Server: `f5networks.f5_modules.bigip_virtual_server`
  - Pools & Members: `f5networks.f5_modules.bigip_pool`, `f5networks.f5_modules.bigip_pool_member`
  - Nodes & SSL: `f5networks.f5_modules.bigip_node`, `f5networks.f5_modules.bigip_ssl_certificate`
  - Always use `provider: "{{ f5_provider }}"` and `delegate_to: localhost`
- **Zscaler Cloud Security**:
  - ZIA (Internet Access): `zscaler.ziacloud.*` (`zia_url_categories`, `zia_url_filtering_rules`, `zia_activation_status` with `status: "ACTIVE"`)
  - ZPA (Private Access / ZTNA): `zscaler.zpacloud.*` (`zpa_application_segment`, `zpa_server_group`)
  - NEVER mix ZIA and ZPA modules across collections!
- **Jira ITSM & Change Management**: `community.general.jira`
  - Always use `operation:` (`create`, `fetch`, `comment`, `transition`), NOT `action:`
  - Use `issue: "OPS-123"` NOT `ticket_id:`
- **Multi-Cloud**:
  - AWS: `amazon.aws.*` (`ec2_instance`, `s3_object`, `route53`)
  - Azure: `azure.azcollection.*` (`azure_rm_virtualmachine`, `azure_rm_virtualnetwork`)
  - GCP: `google.cloud.*` (`gcp_compute_instance`, `gcp_storage_bucket`)
- **Core Linux & System**: `ansible.builtin.*`, `ansible.posix.*` (`firewalld`, `sysctl`, `authorized_key`), `community.general.*` (`ufw`)

### When Unsure About a Module
1. DO NOT guess or invent modules or parameters.
2. Write `# TODO: verify module — could not confirm existence with ansible-doc`.
3. Suggest the exact command: `ansible-doc <FQCN>` or query via the local MCP server.

---

## 2. Task Construction & Idempotency Rules

- Every task MUST have a descriptive `name:` starting with a capital verb (e.g. `Ensure Nginx is started`).
- Add meaningful `tags:` to every task (e.g. `tags: ['f5', 'drain']`).
- Use `become: true` only when privilege escalation is actually needed.
- `command:` and `shell:` tasks MUST include `changed_when:` and preferably `creates:`/`removes:`.
- Prefer specialized modules over `command:` / `shell:` — ALWAYS.
- Handlers MUST be used for service restarts or reloads. Never restart services inline within loops.
- Use `no_log: true` on any task handling passwords, API tokens, private keys, or secrets.

---

## 3. Variable & Data Rules

- Variables in `snake_case` (e.g. `akamai_network`, `f5_provider`).
- Always use `{{ variable | default('fallback') }}` for optional variables.
- In `when:` conditions, use **bare variable names**: `when: is_maintenance_window` — NEVER `when: "{{ is_maintenance_window }}"`.
- File modes MUST be quoted strings: `mode: '0644'`, `mode: '0600'` (never unquoted octals like `0644`).
- Secrets MUST come from Ansible Vault: prefix with `vault_` (e.g. `vault_akamai_client_token`, `vault_f5_password`).

---

## 4. Modern Syntax Rules

- Use `loop:` — NEVER use deprecated `with_items:`, `with_dict:`, or other `with_*` forms.
- Use `ansible.builtin.import_role` / `ansible.builtin.include_role` — NOT bare `roles:` blocks inside conditional logic.
- Use `ansible.builtin.import_tasks` (static) and `ansible.builtin.include_tasks` (dynamic).
- Error handling: Use `block:`, `rescue:`, and `always:` blocks for transactions (e.g. Jira ticket open -> change -> Jira ticket close/fail).

---

## 5. Quick Anti-Hallucination Matrix

| Common Hallucination | Correct Enterprise FQCN & Pattern |
|---|---|
| `akamai_purge` | ✅ `akamai.edgegrid.cache_purge` |
| `akamai_dns` | ✅ `akamai.edgegrid.dns_record` |
| `bigip_pool` | ✅ `f5networks.f5_modules.bigip_pool` |
| `bigip_vip` | ✅ `f5networks.f5_modules.bigip_virtual_server` |
| `zscaler_url_filter` | ✅ `zscaler.ziacloud.zia_url_filtering_rules` |
| `zpa_segment` | ✅ `zscaler.zpacloud.zpa_application_segment` |
| `jira_ticket` | ✅ `community.general.jira` (with `operation: create`) |
| `ec2` or `ec2_instance` | ✅ `amazon.aws.ec2_instance` |
| `azure_vm` | ✅ `azure.azcollection.azure_rm_virtualmachine` |
| `gce` | ✅ `google.cloud.gcp_compute_instance` |
| `docker_container` | ✅ `community.docker.docker_container` |
| `firewalld` | ✅ `ansible.posix.firewalld` |
| `authorized_key` | ✅ `ansible.posix.authorized_key` |
| `sysctl` | ✅ `ansible.posix.sysctl` |
