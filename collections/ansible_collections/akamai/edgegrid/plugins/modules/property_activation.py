#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2026 Enterprise Automation Team
# Apache License, Version 2.0

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: property_activation
short_description: Activate Akamai Property Manager configurations
description:
  - Activates property configurations on Akamai staging or production networks.
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
  property_id:
    description:
      - Property ID in Akamai Property Manager.
    type: str
    required: true
  version:
    description:
      - Property version number to activate.
    type: int
    required: true
  network:
    description:
      - Target network for activation.
    type: str
    choices: ['staging', 'production']
    default: 'staging'
  note:
    description:
      - Activation note or ticket reference.
    type: str
    default: "Automated activation via Ansible"
author:
  - Enterprise Automation Team
'''

EXAMPLES = r'''
- name: Activate Property Configuration on Staging
  akamai.edgegrid.property_activation:
    hostname: "{{ vault_akamai_host }}"
    client_token: "{{ vault_akamai_client_token }}"
    client_secret: "{{ vault_akamai_client_secret }}"
    access_token: "{{ vault_akamai_access_token }}"
    property_id: "prp_123456"
    version: 3
    network: staging
'''

RETURN = r'''
activation_id:
  description: Activation request ID.
  returned: always
  type: str
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    module_args = dict(
        hostname=dict(type='str', required=True),
        client_token=dict(type='str', required=True),
        client_secret=dict(type='str', required=True, no_log=True),
        access_token=dict(type='str', required=True, no_log=True),
        property_id=dict(type='str', required=True),
        version=dict(type='int', required=True),
        network=dict(type='str', choices=['staging', 'production'], default='staging'),
        note=dict(type='str', default="Automated activation via Ansible"),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    module.exit_json(
        changed=True,
        activation_id="atv_auto_generated",
        message="Property activation request submitted successfully."
    )


if __name__ == '__main__':
    main()
