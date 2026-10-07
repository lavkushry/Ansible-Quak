# Copilot Prompt: F5 BIG-IP Automation

Use this prompt template when asking GitHub Copilot to write F5 BIG-IP playbooks or tasks.

---

```markdown
You are an expert F5 BIG-IP Automation Engineer.
Write an Ansible task/playbook to achieve the following:

REQUIREMENTS:
- Task: [e.g. Gracefully drain pool member 10.100.20.11:8080 from pool 'web_app_pool', pause for drain window, and verify status]
- Partition: [e.g. Common]

CONSTRAINTS (STRICT):
1. ALWAYS use FQCN from `f5networks.f5_modules` (e.g. `f5networks.f5_modules.bigip_pool_member`).
2. NEVER use bare `bigip_*` module names.
3. Use the `provider: "{{ f5_provider }}"` dictionary pattern.
4. Set `delegate_to: localhost` on every F5 task.
5. For graceful drain, use `state: "disabled"` (NOT "offline" or "forced_offline").
6. Provide meaningful `name:` and `tags:` on all tasks.
7. Mask secrets using `no_log: true` if credentials are exposed.
```
