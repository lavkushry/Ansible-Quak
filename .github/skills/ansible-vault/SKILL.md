---
name: ansible-vault
description: >
  MANDATORY skill for handling secrets, passwords, API keys, certificates,
  tokens, or any sensitive data in Ansible. Prevents secret leakage.
---

# Ansible Vault: Production-Grade Secrets Management

## Mandatory Pre-Steps
1. Identify all sensitive variables (passwords, tokens, private keys).
2. NEVER hardcode plaintext secrets in playbooks, roles, or inventory.
3. ALWAYS ensure `no_log: true` is set on ANY task that interacts with or processes a secret.

---

## 1. Complete Vault Workflow

**Create a new encrypted file:**
```bash
ansible-vault create group_vars/all/vault.yml
```

**Edit an existing encrypted file:**
```bash
ansible-vault edit group_vars/all/vault.yml
```

**Encrypt an existing plaintext file:**
```bash
ansible-vault encrypt group_vars/all/vault.yml
```

**Decrypt a file temporarily:**
```bash
ansible-vault decrypt group_vars/all/vault.yml
```

**Rekey (change password):**
```bash
ansible-vault rekey group_vars/all/vault.yml
```

---

## 2. Variable Naming Convention

Always prefix vaulted variables with `vault_` in the `vault.yml` file, and assign them to standard variables in `vars.yml`. This abstracts the encryption from the playbook usage.

**group_vars/all/vault.yml** (Encrypted):
```yaml
vault_db_password: "SuperSecretPassword123!"
vault_api_key: "abc123xyz"
```

**group_vars/all/vars.yml** (Plaintext):
```yaml
db_password: "{{ vault_db_password }}"
api_key: "{{ vault_api_key }}"
```

---

## 3. Inline Encryption (`encrypt_string`)

Instead of encrypting an entire file, encrypt individual strings. Highly recommended for mixing safe and secret variables in the same file.

**Command:**
```bash
ansible-vault encrypt_string 'SuperSecret123!' --name 'db_password'
```

**Result in YAML:**
```yaml
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  64343166646532653331663166343537333634336137633261623930336237666236616466653266
  ...
```

---

## 4. Multi-Vault Setup (Vault IDs)

For enterprise environments with multiple environments (dev/prod) or teams:
```bash
# Encrypt using a specific ID
ansible-vault encrypt_string --vault-id prod@prompt 'secret' --name 'prod_secret'

# Run playbook with specific vault passwords
ansible-playbook playbook.yml --vault-id dev@pass_file_dev --vault-id prod@prompt
```

---

## 5. CI/CD Integration Patterns

**GitHub Actions Example:**
Store the Vault password in GitHub Secrets.
```yaml
- name: Run Ansible Playbook
  run: |
    echo "${{ secrets.ANSIBLE_VAULT_PASSWORD }}" > .vault_pass
    ansible-playbook playbook.yml --vault-password-file .vault_pass
  env:
    ANSIBLE_HOST_KEY_CHECKING: 'false'
```

---

## 6. The `no_log: true` Rule (CRITICAL)

If a task uses a secret, it MUST have `no_log: true`. Otherwise, the secret will be dumped in plaintext in Ansible console output and CI/CD logs upon task failure or high verbosity.

**Example:**
```yaml
- name: Create database user
  community.mysql.mysql_user:
    name: myapp
    password: "{{ db_password }}"  # Uses vault secret
    priv: '*.*:ALL'
    state: present
  no_log: true  # MANDATORY
```

---

## 7. Template Security for Secrets

When copying SSL certs, private keys, or templating config files with secrets:
1. Ensure the destination file permissions are secure (`0600` or `0400`).
2. Set ownership correctly.

**Example:**
```yaml
- name: Deploy application config with DB password
  ansible.builtin.template:
    src: app_config.j2
    dest: /etc/myapp/config.yml
    owner: root
    group: root
    mode: '0600'  # MANDATORY for files with secrets
```

---

## 8. Common Mistakes and Pitfalls

1. **Committing unencrypted secrets:** Accidentally `git commit` of a decrypted `vault.yml`. ALWAYS verify git diff before committing.
2. **Forgetting `no_log: true`:** As discussed, leads to catastrophic secret leakage in Jenkins/GitHub/Gitlab logs.
3. **Printing secrets with `debug`:** Never use `ansible.builtin.debug` on a variable that contains a vault secret.
4. **Encrypting templates (.j2 files) entirely:** Do not encrypt the `.j2` file itself. Instead, encrypt the *variables* passed into the template. 

---

## 9. Emergency Rotation Procedure

If a vault password is leaked:
1. Generate a new strong vault password.
2. Run `ansible-vault rekey` across ALL encrypted files.
3. Update the password in CI/CD secret managers.
4. Run playbooks to rotate the actual endpoint secrets (e.g., rotate DB passwords using the new vault).
