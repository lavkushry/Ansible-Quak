# Gemini & Antigravity Rules for Ansible Automation

This workspace enforces strict Enterprise Ansible standards. Refer to [AGENTS.md](./AGENTS.md) for full architecture directives.

## Critical Invariants:
1. **Mandatory FQCN**: All Ansible modules must use their Fully Qualified Collection Name (`f5networks.f5_modules.*`, `akamai.edgegrid.*`, `zscaler.ziacloud.*`, `zscaler.zpacloud.*`, `community.general.jira`, `ansible.builtin.*`, `ansible.posix.*`).
2. **Anti-Overworking**: If the user asks for a task or snippet, output ONLY that specific task block. Do not generate unnecessary playbooks, inventories, or verbose text.
3. **Execution Context**: Always set `delegate_to: localhost` and `no_log: true` on control-plane API modules with credentials.
4. **Validation**: Test tasks with `ansible-lint` and `scripts/verify-modules.sh` using `.venv/bin/ansible`.
