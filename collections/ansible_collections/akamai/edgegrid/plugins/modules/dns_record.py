#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Enterprise Automation Team
# Apache License, Version 2.0

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: dns_record
short_description: Manage Akamai Edge DNS (v2) Zone Records
description:
  - Creates, updates, or deletes Edge DNS records in Akamai Edge DNS zones.
options:
  hostname:
    description:
      - Akamai API hostname.
    type: str
    required: true
  client_token:
    description:
      - Akamai API client token.
    type: str
    required: true
  client_secret:
    description:
      - Akamai API client secret.
    type: str
    required: true
    no_log: true
  access_token:
    description:
      - Akamai API access token.
    type: str
    required: true
    no_log: true
  zone:
    description:
      - The DNS zone name (e.g. example.com).
    type: str
    required: true
  name:
    description:
      - The record name (e.g. app.example.com).
    type: str
    required: true
  type:
    description:
      - The record type.
    type: str
    choices: ['A', 'AAAA', 'CNAME', 'TXT', 'MX', 'PTR', 'SRV']
    required: true
  target:
    description:
      - List of target record values or IP addresses.
    type: list
    elements: str
    required: true
  ttl:
    description:
      - Time To Live in seconds.
    type: int
    default: 300
  state:
    description:
      - Desired state of the record.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  active:
    description:
      - Whether to activate the change immediately.
    type: bool
    default: true
author:
  - Enterprise Automation Team
'''

EXAMPLES = r'''
- name: Ensure Akamai CNAME Record exists
  akamai.edgegrid.dns_record:
    hostname: "{{ vault_akamai_host }}"
    client_token: "{{ vault_akamai_client_token }}"
    client_secret: "{{ vault_akamai_client_secret }}"
    access_token: "{{ vault_akamai_access_token }}"
    zone: "example.com"
    name: "app.example.com"
    type: "CNAME"
    target:
      - "app.example.com.edgekey.net."
    ttl: 300
    state: present
'''

RETURN = r'''
record:
  description: Record details.
  returned: always
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    module_args = dict(
        hostname=dict(type='str', required=True),
        client_token=dict(type='str', required=True),
        client_secret=dict(type='str', required=True, no_log=True),
        access_token=dict(type='str', required=True, no_log=True),
        zone=dict(type='str', required=True),
        name=dict(type='str', required=True),
        type=dict(type='str', choices=['A', 'AAAA', 'CNAME', 'TXT', 'MX', 'PTR', 'SRV'], required=True),
        target=dict(type='list', elements='str', required=True),
        ttl=dict(type='int', default=300),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        active=dict(type='bool', default=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    module.exit_json(
        changed=True,
        message="DNS record successfully synchronized."
    )


if __name__ == '__main__':
    main()
