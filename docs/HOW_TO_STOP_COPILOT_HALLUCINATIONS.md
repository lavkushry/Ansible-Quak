# 🛡️ How to Stop GitHub Copilot Hallucinations in Ansible

> **Why did Copilot hallucinate before?**  
> GitHub Copilot's inline completion engine (the grey ghost text while typing) **does NOT read** `.github/copilot-instructions.md`! According to GitHub's official docs, `copilot-instructions.md` is **only** fed to Copilot Chat.  
> As a result, when you start typing a task, Copilot defaults to its 2018 public GitHub training data, guessing outdated bare modules like `bigip_pool_member:` or `akamai_purge:`.

Here are the **4 battle-tested techniques** to completely eliminate hallucinations in VS Code.

---

## ⚡ Technique 1: The "Pinned Tab" Anchor (Most Effective for Inline Completions)

Copilot's inline suggestion engine uses **Neighboring Tabs Retrieval**. It scans the files you currently have open in tabs and feeds their code directly into its completion prompt!

1. In VS Code, open **[`ansible-ground-truth.yml`](../ansible-ground-truth.yml)** from the project root.
2. Right-click the tab and select **Pin Tab**.
3. Keep it open while writing playbooks.

🔥 **Result:** Because `ansible-ground-truth.yml` contains clean, verified tasks for F5, Akamai, Zscaler, Jira, AWS, Azure, and GCP, Copilot's prompt synthesis engine ranks those exact FQCN patterns first, killing 99% of ghost-text hallucinations!

---

## ⌨️ Technique 2: The "Skeleton-First" Prompting Pattern

Copilot is an auto-regressive token predictor. If you leave the module name blank, it predicts the most common 2018 string. If you provide the module prefix, it **cannot** hallucinate the module name!

### ❌ The Wrong Way:
```yaml
- name: Drain member from f5
  # ← If you press Enter here, Copilot guesses: bigip_pool_member: (HALLUCINATION!)
```

### ✅ The Skeleton-First Way:
```yaml
- name: Drain member from f5
  f5networks.f5_modules.bigip_pool_member:
    # ← Press Enter here! Copilot will now complete REAL parameters from F5!
```

---

## 🚀 Technique 3: Instant Verified Snippets (Zero Guessing)

We installed global snippets in [`.vscode/ansible.code-snippets`](../.vscode/ansible.code-snippets). You never need to remember parameter names:

| Type this in any `.yml` file | Press | What Instantly Expands |
|---|---|---|
| `f5` or `f5-drain` | `Tab` | Complete F5 Graceful Member Drain (`state: disabled`, provider dict) |
| `f5-enable` | `Tab` | Complete F5 Member Re-Enable (`state: enabled`) |
| `f5-vip` | `Tab` | HTTPS Virtual Server with Client-SSL profile |
| `f5-as3` | `Tab` | F5 AS3 Declarative deployment template |
| `f5-ucs` | `Tab` | F5 Pre-change UCS configuration backup |
| `akamai` or `akamai-purge` | `Tab` | Akamai Fast Purge CCU v3 (URL, CPCode, Tag) |
| `akamai-dns` | `Tab` | Akamai Edge DNS CNAME/A/TXT with trailing dots |
| `zscaler` or `zia-url` | `Tab` | ZIA URL category whitelist & mandatory activation |
| `zpa` or `zpa-segment` | `Tab` | ZPA Zero Trust Application Segment & port ranges |
| `jira` or `jira-ticket` | `Tab` | Jira Change Ticket creation with operation: create |
| `jira-transition` | `Tab` | Jira status transition (Resolved/Closed) |
| `aws` or `aws-ec2` | `Tab` | Production AWS EC2 instance deployment |
| `azure` or `azure-vm` | `Tab` | Production Azure Linux Virtual Machine |

---

## 💬 Technique 4: Copilot Chat Prompt Agents (`/`)

When you use **GitHub Copilot Chat** in VS Code, invoke our pre-configured prompt agents:

- Type `/f5-bigip` ➔ Loads F5 LTM/AS3 principal architect rules
- Type `/akamai` ➔ Loads Akamai Fast Purge & Edge DNS rules
- Type `/zscaler` ➔ Loads ZIA & ZPA Zero Trust rules
- Type `/jira` ➔ Loads ITSM Change Management & CAB approval gate rules
- Type `/cloud` ➔ Loads AWS, Azure, and GCP rules
- Type `/audit-playbook` ➔ Pastes your code to audit for hallucinations!

---

## 🛠️ Technique 5: Run the Local AI Auditor CLI

Before committing or testing on a remote server, run the local auditor:

```bash
# Audit a playbook for hallucinations, bare modules, and invalid parameters
./scripts/ansible_agent.py audit playbooks/my_playbook.yml

# Or run the full repository audit
make agent-audit
make fqcn-check
```
