---
name: ansible-troubleshoot
description: >
  Use when debugging failed playbooks, tasks, connectivity issues, or
  unexpected behavior. Covers systematic debugging workflows.
---

# Ansible Troubleshooting & Debugging Guide

## Mandatory Pre-Steps
1. ALWAYS read the exact error message string. Ansible errors contain the specific failing host and variable context.
2. DO NOT blindly rewrite tasks. Identify the root cause (Syntax? Auth? Variable scoping?).

---

## 1. Systematic Debugging Workflow

**Flowchart:**
1. **Is it a connection issue?**
   `ansible all -m ping -i inventory.yml` (For SSH/WinRM verification)
2. **Is it a syntax error?**
   `ansible-playbook playbook.yml --syntax-check`
3. **Is it a module error?**
   `ansible-doc <module_name>` (Verify parameters locally)
4. **Is it a variable issue?**
   Inject the `debug` module before the failing task.
5. **Is it a privilege/permission issue?**
   Check `become: true`, `become_user: root`, and file system permissions.
6. **Is it a Jinja2 error?**
   Verify variable exists and filter syntax (See `ansible-jinja2` skill).

---

## 2. The `debug` Module Techniques

**Print a variable's value:**
```yaml
- name: Inspect variable
  ansible.builtin.debug:
    var: my_complex_dict
```

**Print a message with interpolation and type:**
```yaml
- name: Show variable type
  ansible.builtin.debug:
    msg: "Variable is of type {{ my_var | type_debug }} and value is {{ my_var }}"
```

**Conditional Debug (High Verbosity Only):**
Avoid spamming standard output; only show when `-vv` is used.
```yaml
- name: Deep dive network facts
  ansible.builtin.debug:
    msg: "Interface facts: {{ ansible_default_ipv4 }}"
  verbosity: 2
```

**Save output to a file for massive JSON payloads:**
```yaml
- name: Save output locally
  ansible.builtin.copy:
    content: "{{ task_result | to_nice_json }}"
    dest: "/tmp/debug_output.json"
  delegate_to: localhost
```

---

## 3. Playbook Execution Flags for Debugging

- **`-v`, `-vv`, `-vvv`, `-vvvv`**: Increase verbosity. (Task result -> Connection info -> SSH payload).
- **`--check`**: Dry run. (Will the module change state? Note: command/shell modules skip in check mode unless `check_mode: false`).
- **`--diff`**: Show exactly what changed in files.
- **`--step`**: Interactive execution, prompts before running each task.
- **`--start-at-task="Task Name"`**: Skip everything before a specific task.
- **`--list-tasks` / `--list-tags` / `--list-hosts`**: Pre-flight checks on what Ansible plans to do.

---

## 4. Common Errors and Exact Solutions

**Error:** `"Undefined variable: 'foo' is undefined"`
- **Fix:** Ensure the variable is set in inventory/vars, or use the default filter: `{{ foo | default('bar') }}`. Check scoping.

**Error:** `"MODULE FAILURE"`
- **Fix:** Usually means the module crashed on the remote host (e.g., missing Python dependency). Run with `-vvv` to see the Python traceback. 

**Error:** `"Permission denied"`
- **Fix:** You are missing `become: true` at the task or playbook level. Or SSH user lacks permissions.

**Error:** `"Unreachable"`
- **Fix:** Network issue, SSH key issue, or firewall. Test raw SSH: `ssh -i key.pem user@host`.

**Error:** `"The task includes an option with an undefined variable"`
- **Fix:** Usually happens in a loop or dynamic include where a variable hasn't been instantiated yet.

**Error:** `"no action detected in task"`
- **Fix:** YAML indentation error. The module name (like `ansible.builtin.copy`) must be at the exact same indentation level as `name`.

**Error:** `"couldn't resolve module/action"`
- **Fix:** The module FQCN is wrong (e.g., `ansible.builtin.postgres` instead of `community.postgresql.postgresql_db`), or the collection is not installed.

**Error:** `"Syntax Error while loading YAML"`
- **Fix:** Usually unquoted variables starting a line.
  - *BAD*: `msg: {{ var }}`
  - *GOOD*: `msg: "{{ var }}"`

**Error:** `"handler not found"`
- **Fix:** The string in `notify:` does not EXACTLY MATCH the `name:` of the handler, case sensitive.

---

## 5. Helpful Callback Plugins

Configure these in `ansible.cfg` for better debugging output:
```ini
[defaults]
# Makes output human-readable instead of JSON blobs
stdout_callback = yaml

# Shows task execution times to debug slow playbooks
callbacks_enabled = profile_tasks, timer
```
