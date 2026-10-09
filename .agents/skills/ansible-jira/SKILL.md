---
name: ansible-jira
description: >
  MANDATORY skill for ITSM change management automation with Jira. Covers creating
  change tickets, verifying approval status before running playbooks, updating comments
  with deployment logs, and transitioning issue states using community.general.jira.
---

# Jira ITSM Automation Skill (`community.general.jira`)

## Core Rule: Always Use `community.general.jira`

All Jira interactions in Ansible use `community.general.jira` or `ansible.builtin.uri` for advanced REST API endpoints. Never invent `ansible.builtin.jira` or bare `jira`.

```yaml
# In requirements.yml
collections:
  - name: community.general
    version: ">=9.0.0"
```

---

## 1. Authentication Patterns

### Pattern A: Jira Cloud (API Token + Email)
```yaml
# In group_vars/all/vault.yml
vault_jira_url: "https://yourcompany.atlassian.net"
vault_jira_username: "automation-bot@yourcompany.com"
vault_jira_token: "ATATT3xFfGF0r...your-token"
```

### Pattern B: Jira Server / Data Center (Bearer Token or Username/Password)
```yaml
vault_jira_url: "https://jira.corp.internal"
vault_jira_token: "Bearer-Token-Here"
```

---

## 2. Common Enterprise ITSM Workflows

### Pattern 1: Create Change Request Ticket at Start of Maintenance
```yaml
- name: Create Jira Change Ticket for Infrastructure Maintenance
  community.general.jira:
    uri: "{{ vault_jira_url }}"
    username: "{{ vault_jira_username }}"
    password: "{{ vault_jira_token }}"
    project: "OPS"
    issuetype: "Change Request"
    summary: "[AUTOMATION] OS Upgrade & Network Drain on {{ target_host_group }}"
    description: >
      Automated change executed by Ansible AWX/Automation Controller.
      Pipeline ID: {{ lookup('ansible.builtin.env', 'BUILD_NUMBER', default='Manual-Run') }}
      Playbook: {{ ansible_play_name }}
    operation: create
  delegate_to: localhost
  register: jira_ticket
  no_log: true
  tags: ['jira', 'itsm_start']

- name: Store Created Jira Issue Key
  ansible.builtin.set_fact:
    change_ticket_key: "{{ jira_ticket.meta.key }}"
  tags: ['jira']
```

### Pattern 2: Gate Execution on Ticket Approval Status
Prevent unauthorized playbooks from running if the ticket is NOT approved:
```yaml
- name: Fetch current Jira Ticket status
  community.general.jira:
    uri: "{{ vault_jira_url }}"
    username: "{{ vault_jira_username }}"
    password: "{{ vault_jira_token }}"
    issue: "{{ change_ticket_key }}"
    operation: fetch
  delegate_to: localhost
  register: fetched_issue
  no_log: true
  tags: ['jira', 'approval_gate']

- name: Assert change ticket is approved
  ansible.builtin.assert:
    that:
      - fetched_issue.meta.fields.status.name in ['Approved', 'In Progress', 'Ready for Implementation']
    fail_msg: "CRITICAL: Ticket {{ change_ticket_key }} is in '{{ fetched_issue.meta.fields.status.name }}' status, not Approved!"
  tags: ['jira', 'approval_gate']
```

### Pattern 3: Add Progress Comments During Playbook Execution
```yaml
- name: Log milestone completion to Jira Change Ticket
  community.general.jira:
    uri: "{{ vault_jira_url }}"
    username: "{{ vault_jira_username }}"
    password: "{{ vault_jira_token }}"
    issue: "{{ change_ticket_key }}"
    operation: comment
    comment: >
      ✅ Milestone Reached: All web pool members drained on F5 BIG-IP.
      Proceeding with kernel updates and package patching.
      Timestamp: {{ ansible_date_time.iso8601 }}
  delegate_to: localhost
  no_log: true
  tags: ['jira', 'comment']
```

### Pattern 4: Transition Ticket State (In Progress -> Resolved / Failed)
```yaml
- name: Transition Jira Ticket to 'Resolved'
  community.general.jira:
    uri: "{{ vault_jira_url }}"
    username: "{{ vault_jira_username }}"
    password: "{{ vault_jira_token }}"
    issue: "{{ change_ticket_key }}"
    operation: transition
    status: "Resolved"
    comment: "Automated maintenance completed successfully. All verification checks passed."
  delegate_to: localhost
  no_log: true
  tags: ['jira', 'itsm_close']
```

---

## 3. Robust Error Handling (Block / Rescue with Jira)

Always close or flag the ticket if tasks inside the playbook fail:

```yaml
- name: Execute critical maintenance with Jira incident tracking
  block:
    - name: Mark ticket In Progress
      community.general.jira:
        uri: "{{ vault_jira_url }}"
        username: "{{ vault_jira_username }}"
        password: "{{ vault_jira_token }}"
        issue: "{{ change_ticket_key }}"
        operation: transition
        status: "In Progress"
      delegate_to: localhost
      no_log: true

    - name: Run infrastructure maintenance tasks
      ansible.builtin.include_tasks: perform_maintenance.yml

    - name: Close ticket on success
      community.general.jira:
        uri: "{{ vault_jira_url }}"
        username: "{{ vault_jira_username }}"
        password: "{{ vault_jira_token }}"
        issue: "{{ change_ticket_key }}"
        operation: transition
        status: "Closed"
        comment: "All tasks completed and health checks verified."
      delegate_to: localhost
      no_log: true

  rescue:
    - name: Post failure comment to Jira
      community.general.jira:
        uri: "{{ vault_jira_url }}"
        username: "{{ vault_jira_username }}"
        password: "{{ vault_jira_token }}"
        issue: "{{ change_ticket_key }}"
        operation: comment
        comment: >
          🚨 ALERT: Playbook execution FAILED during maintenance!
          Host: {{ inventory_hostname }}
          Failed Task: {{ ansible_failed_task.name | default('Unknown') }}
          Error Message: {{ ansible_failed_result.msg | default('Unknown error') }}
      delegate_to: localhost
      no_log: true

    - name: Fail the playbook
      ansible.builtin.fail:
        msg: "Aborting run due to error. Failure logged to Jira {{ change_ticket_key }}."
```

---

## 4. Anti-Hallucination: Module Names & Operations

| Hallucinated / Invalid Syntax | Correct Syntax |
|---|---|
| ❌ `ansible.builtin.jira` | ✅ `community.general.jira` |
| ❌ `jira_issue` | ✅ `community.general.jira` with `operation: create` |
| ❌ `action: create` | ✅ `operation: create` (`operation`, not `action`) |
| ❌ `operation: update_status` | ✅ `operation: transition` |
| ❌ `ticket_id: "OPS-123"` | ✅ `issue: "OPS-123"` |

---

## 5. Pre-Flight Checklist
- [ ] Always execute Jira tasks with `delegate_to: localhost`.
- [ ] Protect credentials with `no_log: true`.
- [ ] Verify transition status names in Jira (e.g. "Done" vs "Resolved" vs "Closed" vary by workflow).
