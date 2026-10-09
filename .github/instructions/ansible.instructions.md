---
applyTo:
  - "**/*.yml"
  - "**/*.yaml"
---

# Enterprise Ansible Automation Instructions (FQCN & Anti-Hallucination)

## Critical Constraints
1. **MANDATORY FQCN**: NEVER use legacy short module names. Always use the Fully Qualified Collection Name:
   - Akamai: `akamai.edgegrid.cache_purge`, `akamai.edgegrid.dns_record`, `akamai.edgegrid.property_activation`
   - F5 BIG-IP: `f5networks.f5_modules.bigip_virtual_server`, `f5networks.f5_modules.bigip_pool`, `f5networks.f5_modules.bigip_pool_member`, `f5networks.f5_modules.bigip_as3_deploy`
   - Zscaler ZIA: `zscaler.ziacloud.zia_url_categories`, `zscaler.ziacloud.zia_url_filtering_rules`, `zscaler.ziacloud.zia_activation_status` (with `status: ACTIVE`)
   - Zscaler ZPA: `zscaler.zpacloud.zpa_application_segment`, `zscaler.zpacloud.zpa_server_group`
   - Jira ITSM: `community.general.jira` (with `operation: create|comment|transition`, NOT `action:`)
   - AWS: `amazon.aws.ec2_instance`, `amazon.aws.s3_object`
   - Azure: `azure.azcollection.azure_rm_virtualmachine`
   - GCP: `google.cloud.gcp_compute_instance`
   - Core / POSIX: `ansible.builtin.copy`, `ansible.builtin.template`, `ansible.builtin.service`, `ansible.posix.firewalld`, `ansible.posix.sysctl`

2. **NEVER Invent Modules or Parameters**:
   - If unsure of a parameter, output `# TODO: verify parameter in ansible-doc` rather than hallucinating.
   - For F5 modules, always include `provider: "{{ f5_provider }}"` and `delegate_to: localhost`.
   - In `when:` statements, use bare variable names without curly braces (e.g., `when: maintenance_enabled`).
   - File modes must be quoted strings: `mode: '0644'`.
   - Loops must use `loop:`, NEVER `with_items:`.
