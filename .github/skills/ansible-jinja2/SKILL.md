---
name: ansible-jinja2
description: >
  MANDATORY skill for writing Jinja2 templates, expressions, and filters in Ansible.
  Prevents invented filters, covers all syntax patterns, and includes a complete
  filter reference.
---

# Ansible Jinja2 Deep-Dive Guide

## Mandatory Pre-Steps
1. ALWAYS verify your variable types before applying filters.
2. DO NOT hallucinate filters. Only use the filters explicitly documented here.
3. ALWAYS favor Ansible built-in module parameters over complex Jinja2 templating if a native module handles the logic (e.g., `ansible.builtin.copy` or `ansible.builtin.template` instead of `lineinfile` with massive Jinja logic).

---

## 1. Complete Jinja2 Filter Reference

**String Filters:**
- `lower`, `upper`, `capitalize`, `title`: Case transformations. (e.g., `"foo" | upper`)
- `trim`: Strip leading/trailing whitespace. (e.g., `my_var | trim`)
- `truncate`: Truncate string to length. (e.g., `"long text" | truncate(5)`)
- `replace`: Replace substring. (e.g., `my_var | replace('old', 'new')`)
- `regex_replace`: Regex substitution. (e.g., `var | regex_replace('^(.*)$', '\\1')`)
- `regex_search`, `regex_findall`: Regex matching and extraction.
- `split`, `join`: String <-> List operations. (e.g., `"a,b" | split(',')`, `my_list | join('\n')`)
- `center`, `wordwrap`, `indent`: Text formatting.
- `quote`: Shell quoting. (e.g., `var | quote`)
- `urlencode`: URL encoding.
- `comment`: Prepend comment characters. (e.g., `var | comment(decoration="# ")`)

**Number Filters:**
- `int`, `float`, `round`, `abs`, `max`, `min`, `pow`, `log`, `root` (e.g., `var | int(default=0)`)

**List Filters:**
- `first`, `last`, `length`, `count`, `sort`, `reverse`, `unique`, `flatten`: Basic list manip.
- `union`, `intersect`, `difference`, `symmetric_difference`: Set operations on lists.
- `map`: Apply filter to list elements. (e.g., `list_of_dicts | map(attribute='name') | list`)
- `select`, `reject`, `selectattr`, `rejectattr`: Filtering lists. (e.g., `users | selectattr('active', 'equalto', true) | list`)
- `zip`, `zip_longest`, `product`, `combinations`, `permutations`: Combinatorics.
- `subelements`: Flatten nested lists of dicts.
- `json_query`: JMESPath queries (requires `jmespath` pip package). (e.g., `var | json_query('users[*].name')`)

**Dict Filters:**
- `combine`: Merge dicts. (e.g., `dict1 | combine(dict2, recursive=True)`)
- `dict2items`, `items2dict`: Dict <-> List of key/value dicts conversion.
- `dictsort`: Sort a dictionary by key or value.

**Type Conversion Filters:**
- `bool`: Crucial for 'true'/'false' strings. (e.g., `my_string | bool`)
- `to_json`, `from_json`, `to_yaml`, `from_yaml`, `to_nice_json`, `to_nice_yaml`
- `string`, `list`, `int`, `float`

**Path Filters:**
- `basename`, `dirname`, `expanduser`, `realpath`, `relpath`, `splitext`
- `win_basename`, `win_dirname`, `win_splitdrive`

**Crypto/Hash Filters:**
- `hash('md5')`, `hash('sha1')`, `hash('sha256')`, `checksum`, `password_hash('sha512')`
- `b64encode`, `b64decode`

**Network Filters:**
- `ipaddr`, `ipv4`, `ipv6`, `ipsubnet`, `hwaddr`, `macaddr`, `nthhost` (requires `netaddr`)

**Default/Safety Filters:**
- `default` (alias: `d`): Fallback value. (e.g., `var | default('default_value', true)`)
- `mandatory`: Fail if undefined.
- `ternary`: Inline if/else. (e.g., `(condition) | ternary('true_val', 'false_val')`)
- `type_debug`: Prints the Python type of the variable.
- `random`, `shuffle`

**Ansible-Specific Filters:**
- `to_datetime`, `strftime`: Date manipulation.
- `regex_escape`: Escape regex metacharacters.
- `ansible.builtin.vault`: Encrypt/decrypt vault strings.
- `extract`: Map values from a dictionary using a list of keys.
- `human_readable`, `human_to_bytes`

---

## 2. Jinja2 Tests (Conditions using `is` / `is not`)

Use these in `when` statements or inline conditions:
`defined`, `undefined`, `none`, `boolean`, `integer`, `float`, `number`, `string`, `mapping`, `iterable`, `sequence`, `callable`, `sameas`, `equalto`, `ne`, `lt`, `le`, `gt`, `ge`, `even`, `odd`, `divisibleby`, `in`, `contains`, `match` (regex start), `search` (regex anywhere), `regex` (regex whole), `truthy`, `falsy`, `vault_encrypted`, `changed`, `failed`, `succeeded`, `skipped`, `started`, `finished`, `all`, `any`, `file`, `directory`, `link`, `exists`, `abs`, `same_file`, `mount`.

Example:
```yaml
when: my_var is defined and my_var is match('^prd-.*')
```

---

## 3. Template Syntax Patterns

- **Variables**: `{{ variable_name }}` (never nest `{{ {{ }} }}`)
- **Conditionals**:
  ```jinja2
  {% if env == 'prod' %}
  production_setting=1
  {% elif env == 'dev' %}
  production_setting=0
  {% else %}
  production_setting=-1
  {% endif %}
  ```
- **Loops**:
  ```jinja2
  {% for item in items %}
  - {{ loop.index }}: {{ item }}
  {% endfor %}
  ```
- **Whitespace Control**: Use `{%-` or `-%}` to strip newlines.
- **Set Variable**: `{% set temp_var = item.name + '_' + item.id %}`
- **Raw block** (to avoid interpreting Ansible variables):
  ```jinja2
  {% raw %}
  This {{ will_not_be_evaluated }}
  {% endraw %}
  ```

---

## 4. 10 Most Common Jinja2 Mistakes

1. **`{{ }}` inside `when`**
   - **BAD**: `when: {{ my_var }} == true`
   - **GOOD**: `when: my_var | bool` (Ansible automatically evaluates `when` as Jinja2)

2. **Nested quotes**
   - **BAD**: `msg: "{{ 'User is ' {{ user_name }} }}"`
   - **GOOD**: `msg: "User is {{ user_name }}"`

3. **Missing default for optional variables**
   - **BAD**: `path: "/opt/{{ user_path }}"` (Fails if `user_path` undefined)
   - **GOOD**: `path: "/opt/{{ user_path | default('default_dir') }}"`

4. **String vs boolean comparison**
   - **BAD**: `when: is_active == "true"` (Breaks if `is_active` is actual boolean)
   - **GOOD**: `when: is_active | bool`

5. **Incorrect filter chaining (List conversion)**
   - **BAD**: `my_list | map(attribute='name')` (Returns generator)
   - **GOOD**: `my_list | map(attribute='name') | list`

6. **Using Python methods instead of Jinja2 filters**
   - **BAD**: `{{ my_string.split(',') }}`
   - **GOOD**: `{{ my_string | split(',') }}`

7. **Forgetting loop variable scoping**
   Variables defined with `{% set %}` inside a `for` loop do not persist outside it.

8. **Wrong use of `omit` filter**
   - **GOOD**: `mode: "{{ file_mode | default(omit) }}"` (MUST be default(omit))

9. **Multline YAML with Jinja2**
   - **BAD**:
     ```yaml
     copy:
       content: "{{ big_multiline_string }}"
     ```
   - **GOOD**:
     ```yaml
     copy:
       content: >
         {{ big_multiline_string }}
     ```

10. **Inline vs Template files**
    Be careful using `| regex_replace` in standard playbook YAML due to escaping rules `\\` vs `\`. Use `ansible.builtin.template` for heavy text manipulation.

---

## 5. Anti-Hallucination: Invented Filters That DO NOT Exist

AI models frequently hallucinate Jinja filters. NEVER USE THESE:
- ❌ `to_list` → ✅ use `list` or `| list`
- ❌ `to_dict` → ✅ use `items2dict` or `dict()`
- ❌ `format_date` → ✅ use `to_datetime` or `strftime`
- ❌ `titlecase` → ✅ use `title`
- ❌ `strip` → ✅ use `trim`
- ❌ `contains` → ✅ use `in` test (e.g., `when: "'foo' in my_string"`)
- ❌ `startswith` → ✅ use `match` test (e.g., `when: var is match('^prefix')`)
- ❌ `endswith` → ✅ use `search` test (e.g., `when: var is search('suffix$')`)
- ❌ `to_bool` → ✅ use `bool`
- ❌ `to_int` → ✅ use `int`
