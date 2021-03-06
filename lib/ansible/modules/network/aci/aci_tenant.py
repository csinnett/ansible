#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: aci_tenant
short_description: Manage tenants on Cisco ACI fabrics
description:
- Manage tenants on a Cisco ACI fabric.
author:
- Swetha Chunduri (@schunduri)
- Dag Wieers (@dagwieers)
version_added: '2.4'
requirements:
- ACI Fabric 1.0(3f)+
options:
  tenant_name:
    description:
    - The name of the tenant.
    required: yes
  description:
    description:
    - Description for the Tenant.
  state:
    description:
    - present, absent, query
    default: present
    choices: [ absent, present, query ]
extends_documentation_fragment: aci
'''

EXAMPLES = r'''
- name: Add a new tenant
  aci_tenant:
    hostname: apic
    username: admin
    password: SomeSecretPassword
    tenant_name: Name of the tenant
    description: Description for the tenant
    state: present

- name: Remove a tenant
  aci_tenant:
    hostname: apic
    username: admin
    password: SomeSecretPassword
    tenant_name: Name of the tenant
    state: absent

- name: Query a tenant
  aci_tenant:
    hostname: apic
    username: admin
    password: SomeSecretPassword
    tenant_name: Name of the tenant
    state: query

- name: Query all tenants
  aci_tenant:
    hostname: apic
    username: admin
    password: SomeSecretPassword
    state: query
'''

RETURN = r'''
status:
  description: The status code of the http request
  returned: upon making a successful GET, POST or DELETE request to the APIC
  type: int
  sample: 200
response:
  description: Response text returned by APIC
  returned: when a HTTP request has been made to APIC
  type: string
  sample: '{"totalCount":"0","imdata":[]}'
'''

import json

from ansible.module_utils.aci import ACIModule, aci_argument_spec
from ansible.module_utils.basic import AnsibleModule


def main():
    argument_spec = aci_argument_spec
    argument_spec.update(
        tenant_name=dict(type='str', aliases=['name']),
        description=dict(type='str', aliases=['descr']),
        state=dict(type='str', default='present', choices=['absent', 'present', 'query']),
        method=dict(type='str', choices=['delete', 'get', 'post'], aliases=['action'], removed_in_version='2.6'),  # Deprecated starting from v2.6
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    tenant_name = module.params['tenant_name']
    description = str(module.params['description'])
    state = module.params['state']

    aci = ACIModule(module)

    if tenant_name is not None:
        # Work with a specific tenant
        path = 'api/mo/uni/tn-%(tenant_name)s.json' % module.params
    elif state == 'query':
        # Query all tenants
        path = 'api/node/class/fvTenant.json'
    else:
        module.fail_json("Parameter 'tenant_name' is required for state 'absent' or 'present'")

    if state == 'query':
        aci.request(path)
    elif module.check_mode:
        # TODO: Implement proper check-mode (presence check)
        aci.result(changed=True, response='OK (Check mode)', status=200)
    else:
        payload = {'fvTenant': {'attributes': {'name': tenant_name, 'descr': description}}}
        aci.request_diff(path, payload=json.dumps(payload))

    module.exit_json(**aci.result)

if __name__ == "__main__":
    main()
