# 🛡️ Ansible-Quak: Enterprise Anti-Hallucination Ansible Framework

> **Production-Grade Ansible Automation for Enterprise Network, Cloud & Security Engineering.**  
> Powered by **VS Code Copilot Prompt Agents, AST Schema Validation, CLI Scaffolding Agents, and CI/CD Gates** to permanently eliminate AI hallucinations across **F5 BIG-IP, Akamai CDN, Zscaler Zero Trust, Jira ITSM, AWS, Azure, and GCP**.

---

## 🎯 The Core Problem & The Solution

In enterprise automation, AI assistants (GitHub Copilot, ChatGPT, Claude) frequently hallucinate:
- **Invented module names** (`akamai_purge`, `bigip_pool`, `jira_ticket`)
- **Invalid parameter names** (`action: create` instead of `operation: create`, `state: offline` instead of `disabled`)
- **Missing FQCNs** (`copy` instead of `ansible.builtin.copy`)
- **Jinja2 syntax errors** (`when: "{{ my_var == true }}"`)
- **Unmasked credentials** (exposing API keys in debug/playbook logs)

**Ansible-Quak** solves this with a **Dual-Agent Architecture**:
1. **Interactive Prompt Agents in VS Code Copilot Chat** (`.github/prompts/*.prompt.md`)
2. **Local Python AST Agent & Auditor** (`scripts/ansible_agent.py`)

---

## 🤖 7 Specialized VS Code Copilot Agents (`.github/prompts/`)

When using **GitHub Copilot Chat in VS Code**, select these agents directly using `/` or attach them to your prompt:

| Agent Prompt File | Shortcut | Purpose & Guardrails |
|---|---|---|
| **[`f5-bigip.prompt.md`](.github/prompts/f5-bigip.prompt.md)** | `/f5-bigip` | F5 BIG-IP LTM/DNS, Declarative AS3, Graceful Pool Drain (`state: disabled`), VIPs, SSL Certs, HA Sync |
| **[`akamai.prompt.md`](.github/prompts/akamai.prompt.md)** | `/akamai` | Akamai Fast Purge CCU v3 (URL/CPCode/Tag), Edge DNS (trailing dots on CNAMEs), Property Manager (PAPI) |
| **[`zscaler.prompt.md`](.github/prompts/zscaler.prompt.md)** | `/zscaler` | Zero Trust Security: Separates ZIA (`zscaler.ziacloud`) and ZPA (`zscaler.zpacloud`), URL categories, App Segments |
| **[`jira.prompt.md`](.github/prompts/jira.prompt.md)** | `/jira` | ITSM Change Management: Ticket creation, CAB Approval Gates, Progress Logging, and Rescue Rollback |
| **[`cloud.prompt.md`](.github/prompts/cloud.prompt.md)** | `/cloud` | Multi-Cloud: AWS (`amazon.aws`), Azure (`azure.azcollection`), GCP (`google.cloud`) with Transit Gateways |
| **[`audit-playbook.prompt.md`](.github/prompts/audit-playbook.prompt.md)** | `/audit-playbook` | Audits any playbook/role for bare modules, parameter typos, missing `no_log`, and idempotency defects |
| **[`playbook-architect.prompt.md`](.github/prompts/playbook-architect.prompt.md)** | `/playbook-architect` | End-to-end multi-vendor orchestrations connecting Jira + F5 + Zscaler + Akamai + Cloud |

---

## ⚡ Interactive Local CLI Agent (`scripts/ansible_agent.py`)

Run the local AI agent directly from your terminal to scaffold production tasks or audit playbooks in seconds:

```bash
# 1. List all available verified task templates
./scripts/ansible_agent.py list

# 2. Scaffold a graceful F5 pool member drain task
./scripts/ansible_agent.py scaffold --type f5 --action drain

# 3. Scaffold an Akamai Fast Purge task
./scripts/ansible_agent.py scaffold --type akamai --action purge

# 4. Scaffold a Zscaler ZPA Application Segment task
./scripts/ansible_agent.py scaffold --type zscaler --action zpa-segment

# 5. Scaffold a Jira Change Request & CAB Approval Gate
./scripts/ansible_agent.py scaffold --type jira --action change-gate

# 6. Audit ANY playbook in your repository for hallucinations & syntax defects
./scripts/ansible_agent.py audit playbooks/enterprise_edge_datacenter_orchestration.yml
```

---

## 🏗️ 4 Enterprise Production Roles in `roles/`

Pre-built, modular enterprise roles that serve as **few-shot context** for GitHub Copilot:

- **[`roles/f5_bigip_maintenance/`](roles/f5_bigip_maintenance)**: Takes UCS backup, gracefully drains pool members, re-enables members, and triggers HA config-sync.
- **[`roles/akamai_edge_operations/`](roles/akamai_edge_operations)**: Executes Fast Purge (url, cpcode, tag) and configures Edge DNS records.
- **[`roles/zscaler_policy_manager/`](roles/zscaler_policy_manager)**: Manages ZIA URL categories, commits policy activations, and provisions ZPA Application Segments.
- **[`roles/jira_itsm_lifecycle/`](roles/jira_itsm_lifecycle)**: Creates change tickets, gates execution on CAB approval, posts milestone comments, and transitions statuses.

---

## ⌨️ VS Code Snippets (`.vscode/ansible.code-snippets`)

Type these prefixes in any `.yml` file in VS Code for instant, non-hallucinated completions:
- `f5-drain` ➔ F5 Graceful Pool Member Drain
- `f5-enable` ➔ F5 Pool Member Enable
- `f5-as3` ➔ F5 Declarative AS3 Application Deployment
- `akamai-purge` ➔ Akamai Fast Purge CCU v3
- `akamai-dns` ➔ Akamai Edge DNS Record
- `zscaler-zia-url` ➔ ZIA Custom URL Category & Activation
- `zscaler-zpa-segment` ➔ ZPA Zero Trust Application Segment
- `jira-ticket` ➔ Jira ITSM Change Ticket
- `jira-transition` ➔ Jira Status Transition
- `aws-ec2` ➔ AWS EC2 Instance Deployment

---

## 🔍 Validation Suite & Makefile Commands

```bash
# Run AST-based FQCN anti-hallucination scan
make fqcn-check

# Run AI Agent AST audit across all playbooks
make agent-audit

# Run full multi-stage validation
make validate
```

---

## 🚀 Push to GitHub

```bash
git add .
git commit -m "feat: complete enterprise prompt agents, CLI assistant, and VS Code integration"
git push origin main
```

---

## 📄 License
MIT
