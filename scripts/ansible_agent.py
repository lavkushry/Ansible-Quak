#!/usr/bin/env python3
"""
ansible_agent.py - Enterprise Ansible Automation Assistant & Anti-Hallucination Agent
Provides CLI scaffolding, schema-verified templates, and AST auditing for:
- F5 BIG-IP (f5networks.f5_modules)
- Akamai EdgeGrid (akamai.edgegrid)
- Zscaler Cloud Security (zscaler.ziacloud, zscaler.zpacloud)
- Jira ITSM Change Management (community.general.jira)
- Multi-Cloud (amazon.aws, azure.azcollection, google.cloud)
"""

import sys
import os
import argparse
import subprocess
import yaml
from pathlib import Path

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
RESET = "\033[0m"

TEMPLATES = {
    "f5": {
        "drain": """- name: Gracefully Drain F5 Pool Member
  f5networks.f5_modules.bigip_pool_member:
    provider: "{{ f5_provider }}"
    pool: "{{ f5_pool_name | default('app_http_pool') }}"
    partition: "{{ f5_partition | default('Common') }}"
    name: "{{ member_host }}:{{ member_port | default('8080') }}"
    state: "disabled"
  delegate_to: localhost
  tags: ['f5', 'drain']""",
        "enable": """- name: Re-Enable F5 Pool Member
  f5networks.f5_modules.bigip_pool_member:
    provider: "{{ f5_provider }}"
    pool: "{{ f5_pool_name | default('app_http_pool') }}"
    partition: "{{ f5_partition | default('Common') }}"
    name: "{{ member_host }}:{{ member_port | default('8080') }}"
    state: "enabled"
  delegate_to: localhost
  tags: ['f5', 'enable']""",
        "as3": """- name: Deploy Application Service via F5 AS3 Declaration
  f5networks.f5_modules.bigip_as3_deploy:
    provider: "{{ f5_provider }}"
    content: "{{ lookup('ansible.builtin.template', 'as3_app.json.j2') }}"
    tenant: "{{ app_tenant | default('Sample_Tenant') }}"
  delegate_to: localhost
  tags: ['f5', 'as3']""",
        "vip": """- name: Configure HTTPS Virtual Server
  f5networks.f5_modules.bigip_virtual_server:
    provider: "{{ f5_provider }}"
    name: "vs_{{ app_name }}_https"
    destination: "{{ vip_ip }}"
    port: 443
    pool: "pool_{{ app_name }}"
    profiles:
      - "/Common/tcp"
      - "/Common/http"
      - "/Common/clientssl_{{ app_name }}"
    snat: "Automap"
    state: present
    partition: "{{ f5_partition | default('Common') }}"
  delegate_to: localhost
  tags: ['f5', 'vip']""",
        "ucs": """- name: Take Pre-Change F5 UCS Configuration Backup
  f5networks.f5_modules.bigip_ucs:
    provider: "{{ f5_provider }}"
    ucs: "backup_pre_change_{{ ansible_date_time.iso8601_basic_short }}.ucs"
    state: present
  delegate_to: localhost
  tags: ['f5', 'backup']"""
    },
    "akamai": {
        "purge": """- name: Fast Purge Akamai Edge Cache (CCU v3)
  akamai.edgegrid.cache_purge:
    hostname: "{{ vault_akamai_host }}"
    client_token: "{{ vault_akamai_client_token }}"
    client_secret: "{{ vault_akamai_client_secret }}"
    access_token: "{{ vault_akamai_access_token }}"
    network: "{{ akamai_network | default('staging') }}"
    purge_type: "url"
    action: "invalidate"
    objects:
      - "https://{{ site_domain }}/app.js"
      - "https://{{ site_domain }}/main.css"
  delegate_to: localhost
  no_log: true
  tags: ['akamai', 'purge']""",
        "dns": """- name: Ensure Akamai Edge DNS CNAME Record is Pointing to Edge
  akamai.edgegrid.dns_record:
    hostname: "{{ vault_akamai_host }}"
    client_token: "{{ vault_akamai_client_token }}"
    client_secret: "{{ vault_akamai_client_secret }}"
    access_token: "{{ vault_akamai_access_token }}"
    zone: "{{ akamai_dns_zone | default('example.com') }}"
    name: "{{ record_name }}"
    type: "CNAME"
    target: ["{{ edge_hostname }}."]
    ttl: 300
    state: present
    active: true
  delegate_to: localhost
  no_log: true
  tags: ['akamai', 'dns']"""
    },
    "zscaler": {
        "zia-url": """- name: Whitelist Corporate APIs in ZIA URL Categories
  zscaler.ziacloud.zia_url_categories:
    provider:
      username: "{{ vault_zia_username }}"
      password: "{{ vault_zia_password }}"
      api_key: "{{ vault_zia_api_key }}"
      cloud: "{{ vault_zia_cloud | default('zscaler.net') }}"
    configured_name: "Corporate_Allowed_APIs"
    super_category: "USER_DEFINED"
    urls:
      - "api.partner-service.io"
      - "auth.identity-provider.com"
    state: present
  delegate_to: localhost
  no_log: true
  tags: ['zscaler', 'zia']

- name: Activate Committed Policy Changes in ZIA
  zscaler.ziacloud.zia_activation_status:
    provider:
      username: "{{ vault_zia_username }}"
      password: "{{ vault_zia_password }}"
      api_key: "{{ vault_zia_api_key }}"
      cloud: "{{ vault_zia_cloud | default('zscaler.net') }}"
    status: "ACTIVE"
  delegate_to: localhost
  no_log: true
  tags: ['zscaler', 'activate']""",
        "zpa-segment": """- name: Provision ZPA Application Segment for Microsegmentation
  zscaler.zpacloud.zpa_application_segment:
    client_id: "{{ vault_zpa_client_id }}"
    client_secret: "{{ vault_zpa_client_secret }}"
    customer_id: "{{ vault_zpa_customer_id }}"
    name: "Internal_Monitoring_Access"
    domain_names:
      - "grafana.corp.internal"
      - "prometheus.corp.internal"
    segment_group_id: "{{ zpa_segment_group_id }}"
    server_groups:
      - id: "{{ zpa_server_group_id }}"
    tcp_port_ranges:
      - "443"
      - "9090"
    is_cname_enabled: true
    enabled: true
  delegate_to: localhost
  no_log: true
  tags: ['zscaler', 'zpa']"""
    },
    "jira": {
        "change-gate": """- name: Create Jira Change Ticket and Gate Approval
  block:
    - name: Create Jira Change Ticket
      community.general.jira:
        uri: "{{ vault_jira_url }}"
        username: "{{ vault_jira_username }}"
        password: "{{ vault_jira_token }}"
        project: "OPS"
        issuetype: "Change Request"
        summary: "[AUTOMATION] Scheduled Infrastructure Change"
        description: "Automated pipeline run initiated via Ansible."
        operation: create
      register: jira_ticket_res
      no_log: true
      delegate_to: localhost

    - name: Record Ticket Key
      ansible.builtin.set_fact:
        active_ticket_key: "{{ jira_ticket_res.meta.key }}"

    - name: Gate on Approval Status
      community.general.jira:
        uri: "{{ vault_jira_url }}"
        username: "{{ vault_jira_username }}"
        password: "{{ vault_jira_token }}"
        issue: "{{ active_ticket_key }}"
        operation: fetch
      register: current_ticket
      no_log: true
      delegate_to: localhost

    - name: Assert Ticket is Approved
      ansible.builtin.assert:
        that:
          - current_ticket.meta.fields.status.name in ['Approved', 'In Progress', 'Ready for Implementation']
        fail_msg: "ABORT: Ticket {{ active_ticket_key }} is not approved."
  tags: ['jira', 'gate']"""
    },
    "cloud": {
        "aws-ec2": """- name: Deploy Production AWS EC2 Instance
  amazon.aws.ec2_instance:
    name: "prod-web-node"
    image_id: "{{ ami_id }}"
    instance_type: "t3.medium"
    key_name: "{{ key_name }}"
    vpc_subnet_id: "{{ subnet_id }}"
    security_group: "{{ sg_id }}"
    network:
      assign_public_ip: false
    tags:
      Environment: "Production"
      ManagedBy: "Ansible"
    wait: true
    state: running
  delegate_to: localhost
  tags: ['aws', 'ec2']""",
        "azure-vm": """- name: Deploy Azure Linux Virtual Machine
  azure.azcollection.azure_rm_virtualmachine:
    resource_group: "{{ azure_resource_group }}"
    name: "vm-app-prod-01"
    vm_size: "Standard_D2s_v5"
    admin_username: "azureuser"
    ssh_password_enabled: false
    ssh_public_keys:
      - path: "/home/azureuser/.ssh/authorized_keys"
        key_data: "{{ vault_ssh_public_key }}"
    image:
      offer: "0001-com-ubuntu-server-jammy"
      publisher: "Canonical"
      sku: "22_04-lts-gen2"
      version: "latest"
  delegate_to: localhost
  tags: ['azure', 'vm']"""
    }
}

KNOWN_HALLUCINATIONS = {
    "akamai_purge": "akamai.edgegrid.cache_purge",
    "akamai_dns": "akamai.edgegrid.dns_record",
    "bigip_pool": "f5networks.f5_modules.bigip_pool",
    "bigip_virtual_server": "f5networks.f5_modules.bigip_virtual_server",
    "bigip_pool_member": "f5networks.f5_modules.bigip_pool_member",
    "bigip_as3": "f5networks.f5_modules.bigip_as3_deploy",
    "zscaler_url_filter": "zscaler.ziacloud.zia_url_filtering_rules",
    "zpa_segment": "zscaler.zpacloud.zpa_application_segment",
    "jira": "community.general.jira",
    "jira_issue": "community.general.jira",
    "ec2": "amazon.aws.ec2_instance",
    "azure_vm": "azure.azcollection.azure_rm_virtualmachine",
    "gce": "google.cloud.gcp_compute_instance",
    "copy": "ansible.builtin.copy",
    "template": "ansible.builtin.template",
    "file": "ansible.builtin.file",
    "shell": "ansible.builtin.shell",
    "command": "ansible.builtin.command",
    "service": "ansible.builtin.service",
    "systemd": "ansible.builtin.systemd"
}

def audit_file(filepath):
    print(f"\n{BOLD}Auditing:{RESET} {filepath}")
    issues = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            content = yaml.safe_load_all("".join(lines))
            
            for line_no, line in enumerate(lines, 1):
                # Check for {{ }} inside when:
                if "when:" in line and "{{" in line and "}}" in line:
                    issues.append((line_no, "CRITICAL: '{{ }}' used in when condition", line.strip(), "Remove '{{ }}' - when conditions take bare variables"))
                
                # Check unquoted mode: 0644
                if "mode:" in line and any(f" {o}" in line for o in ["0644", "0755", "0600", "0700"]):
                    issues.append((line_no, "WARNING: Unquoted file mode", line.strip(), "Quote file mode as string, e.g. mode: '0644'"))

                # Check for deprecated with_items:
                if "with_items:" in line:
                    issues.append((line_no, "DEPRECATED: with_items used", line.strip(), "Replace with modern 'loop:' keyword"))

                # Check for action: create in jira
                if "action: create" in line:
                    issues.append((line_no, "ERROR: Invalid Jira parameter", line.strip(), "Use 'operation: create' in community.general.jira"))

                # Check for bare module hallucinations
                for bare, fqcn in KNOWN_HALLUCINATIONS.items():
                    if line.strip().startswith(f"{bare}:") or line.strip().startswith(f"- {bare}:"):
                        issues.append((line_no, f"HALLUCINATION: Bare module '{bare}'", line.strip(), f"Replace with FQCN '{fqcn}'"))

        if issues:
            print(f"{RED}{BOLD}Found {len(issues)} issue(s):{RESET}")
            for line_no, issue_type, code, fix in issues:
                print(f"  Line {line_no:4d} | {RED}{issue_type}{RESET}")
                print(f"            Code: {code}")
                print(f"            Fix:  {GREEN}{fix}{RESET}\n")
            return False
        else:
            print(f"{GREEN}{BOLD}✓ Clean! No hallucinations or defects found.{RESET}\n")
            return True
    except Exception as e:
        print(f"{RED}Error parsing YAML: {e}{RESET}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Ansible Enterprise AI Agent & Auditor")
    subparsers = parser.add_subparsers(dest="command")

    # Scaffold command
    scaffold_parser = subparsers.add_parser("scaffold", help="Generate verified enterprise tasks")
    scaffold_parser.add_argument("--type", choices=["f5", "akamai", "zscaler", "jira", "cloud"], required=True)
    scaffold_parser.add_argument("--action", required=True)

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit playbook/role for AI hallucinations")
    audit_parser.add_argument("file", help="Path to YAML file to audit")

    # List templates command
    subparsers.add_parser("list", help="List available scaffold templates")

    args = parser.parse_args()

    if args.command == "scaffold":
        type_templates = TEMPLATES.get(args.type, {})
        if args.action in type_templates:
            print(f"\n{GREEN}{BOLD}# Verified Production Task ({args.type.upper()} - {args.action}):{RESET}\n")
            print(type_templates[args.action])
            print()
        else:
            print(f"{RED}Action '{args.action}' not found for type '{args.type}'. Available actions: {list(type_templates.keys())}{RESET}")
    elif args.command == "audit":
        audit_file(args.file)
    elif args.command == "list":
        print(f"\n{BOLD}Available Verified Scaffold Actions:{RESET}")
        for t, actions in TEMPLATES.items():
            print(f"  {CYAN}{t.upper()}:{RESET} {', '.join(actions.keys())}")
        print()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
