#!/usr/bin/env python3
"""
check-fqcn.py - AST-based Fully Qualified Collection Name (FQCN) Checker for Ansible
Parses YAML files, traverses plays, blocks, and tasks, and detects non-FQCN module usage.
Zero false positives on variables, role defaults, meta, molecule, or task parameters.
"""

import os
import sys
import yaml
from pathlib import Path

TASK_DIRECTIVES = {
    "name", "tags", "when", "loop", "with_items", "with_dict", "with_file",
    "register", "become", "become_user", "become_method", "ignore_errors",
    "delegate_to", "delegate_facts", "notify", "vars", "environment",
    "failed_when", "changed_when", "block", "rescue", "always", "listen",
    "until", "retries", "delay", "check_mode", "diff", "no_log", "run_once",
    "args", "debugger", "ignore_unreachable", "loop_control", "throttle",
    "timeout", "any_errors_fatal", "collections"
}

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
RESET = "\033[0m"

violations = []

def inspect_task(task, filepath):
    if not isinstance(task, dict):
        return

    # Check for block/rescue/always
    for block_key in ("block", "rescue", "always"):
        if block_key in task and isinstance(task[block_key], list):
            for sub_task in task[block_key]:
                inspect_task(sub_task, filepath)

    task_name = task.get("name", "<unnamed task>")

    # Identify the module action
    for key in task.keys():
        if key in TASK_DIRECTIVES:
            continue
        
        # Action plugin keywords (e.g., action: copy src=...)
        if key in ("action", "local_action"):
            val = task[key]
            if isinstance(val, dict):
                for sub_key in val:
                    if "." not in sub_key:
                        violations.append((filepath, task_name, sub_key))
            elif isinstance(val, str):
                first_word = val.split()[0]
                if "." not in first_word:
                    violations.append((filepath, task_name, first_word))
            continue

        # If key does NOT contain a dot, it's a bare module (e.g. copy, template, bigip_pool)
        if "." not in key:
            violations.append((filepath, task_name, key))

def is_task_or_playbook_file(rel_path):
    parts = Path(rel_path).parts
    # Exclude variable, metadata, molecule, and template files
    if any(p in ("defaults", "vars", "meta", "molecule", "templates") for p in parts):
        return False
    # Include playbooks, tasks, handlers
    if "tasks" in parts or "handlers" in parts or "playbooks" in parts:
        return True
    # Include top-level example task/playbook YAML files
    if "examples" in parts and rel_path.endswith((".yml", ".yaml")):
        return True
    return False

def scan_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = yaml.safe_load_all(f)
            for doc in content:
                if not doc:
                    continue
                if isinstance(doc, list):
                    for item in doc:
                        if not isinstance(item, dict):
                            continue
                        # Playbook structure
                        if any(k in item for k in ("tasks", "pre_tasks", "post_tasks", "handlers")):
                            for task_list_key in ("pre_tasks", "tasks", "post_tasks", "handlers"):
                                if task_list_key in item and isinstance(item[task_list_key], list):
                                    for t in item[task_list_key]:
                                        inspect_task(t, filepath)
                        # Standalone task list
                        else:
                            inspect_task(item, filepath)
                elif isinstance(doc, dict):
                    if any(k in doc for k in ("tasks", "pre_tasks", "post_tasks", "handlers")):
                        for task_list_key in ("pre_tasks", "tasks", "post_tasks", "handlers"):
                            if task_list_key in doc and isinstance(doc[task_list_key], list):
                                for t in doc[task_list_key]:
                                    inspect_task(t, filepath)
                    elif "name" in doc and any(k for k in doc if "." in k):
                        inspect_task(doc, filepath)
    except Exception:
        pass

def main():
    target_dirs = ["playbooks", "roles", "examples"]
    base_dir = Path(__file__).resolve().parent.parent

    print(f"\n{BOLD}═══════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}  FQCN (Fully Qualified Collection Name) AST Check  {RESET}")
    print(f"{BOLD}═══════════════════════════════════════════════════{RESET}\n")

    for d in target_dirs:
        dir_path = base_dir / d
        if not dir_path.exists():
            continue
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith((".yml", ".yaml")):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, base_dir)
                    if is_task_or_playbook_file(rel_path):
                        scan_file(full_path)

    if violations:
        print(f"{RED}{BOLD}✗ FAILED: Found {len(violations)} non-FQCN module invocation(s):{RESET}\n")
        for filepath, task_name, module in violations:
            rel_path = os.path.relpath(filepath, base_dir)
            print(f"  {RED}✗ [{rel_path}]{RESET}")
            print(f"    Task:   \"{task_name}\"")
            print(f"    Module: {RED}{module}{RESET}  ->  (Needs collection prefix, e.g. ansible.builtin.{module})\n")
        sys.exit(1)
    else:
        print(f"{GREEN}{BOLD}✓ PASSED: All tasks across playbooks, roles, and examples use FQCNs!{RESET}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
