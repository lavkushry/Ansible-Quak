# Copilot Prompt: Jira ITSM Change Management Wrapper

Use this prompt template when asking GitHub Copilot to wrap an Ansible playbook in an automated Jira Change Request lifecycle.

---

```markdown
You are an expert ITSM Automation Engineer.
Write an Ansible playbook block/rescue wrapper for Jira change management.

REQUIREMENTS:
- Jira Project: [e.g. OPS or CHG]
- Issue Type: [Change Request]
- Summary: [e.g. Scheduled Application Deployment]
- Core Tasks: [Insert the technical tasks to execute during the window]

CONSTRAINTS (STRICT):
1. ALWAYS use `community.general.jira` (NEVER `jira` or `ansible.builtin.jira`).
2. Use `operation:` (create, comment, transition, fetch) — NEVER `action:`.
3. Use `issue: "{{ ticket_key }}"` — NEVER `ticket_id:`.
4. Wrap all maintenance tasks in a `block:` / `rescue:` structure.
5. In `rescue:`, post an incident comment with `{{ ansible_failed_task.name }}` and `{{ ansible_failed_result.msg }}`.
6. In `block:` end, transition ticket to 'Resolved' or 'Closed'.
7. Set `delegate_to: localhost` and `no_log: true` on all Jira tasks.
```
