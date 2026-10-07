# Create Playbook

Please create an Ansible playbook based on the following requirements and constraints.

## Context
<!-- Paste your requirements.yml or describe the collections available here -->

## Requirements
<!-- Describe what the playbook should do -->

## Constraints
1. **Always use FQCN** (Fully Qualified Collection Name) for every module (e.g., `ansible.builtin.apt` instead of `apt`).
2. Use variables in `snake_case`.
3. Do not hardcode secrets.
4. Add relevant `tags` to all tasks.
5. Use handlers for restarts where appropriate.
6. Ensure the code is idempotent.

## Output Format
Provide the complete, well-commented YAML for the playbook.

## Validation
Please double-check that every module used includes its FQCN and exists in the specified collections.
