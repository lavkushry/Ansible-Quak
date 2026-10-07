#!/usr/bin/env bash
# ============================================================================
# verify-modules.sh — Verify all FQCN modules in task files actually exist
# ============================================================================
# Extracts module FQCNs from YAML task files and verifies each one exists
# via `ansible-doc`. Catches hallucinated module names that pass FQCN syntax
# checks but reference modules that don't actually exist.
# ============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "═══════════════════════════════════════════════════"
echo "  Module Existence Verification"
echo "═══════════════════════════════════════════════════"
echo ""

# Check if ansible-doc is available
if ! command -v ansible-doc &> /dev/null; then
    echo -e "${YELLOW}⚠ ansible-doc not found. Install Ansible to enable module verification.${NC}"
    exit 0
fi

SCAN_DIRS=()
for dir in playbooks roles examples; do
    if [ -d "$dir" ]; then
        SCAN_DIRS+=("$dir")
    fi
done

if [ ${#SCAN_DIRS[@]} -eq 0 ]; then
    echo -e "${YELLOW}No directories to scan. Skipping.${NC}"
    exit 0
fi

# Extract FQCN module names from YAML files
# Pattern: lines with 2+ spaces followed by a dotted.module.name followed by colon
MODULES=$(grep -rhE '^[[:space:]]+[a-z_]+\.[a-z_]+\.[a-z_]+:' "${SCAN_DIRS[@]}" \
    --include='*.yml' --include='*.yaml' 2>/dev/null \
    | sed -E 's/^[[:space:]]+([a-z_]+\.[a-z_]+\.[a-z_]+):.*/\1/' \
    | sort -u \
    || true)

if [ -z "$MODULES" ]; then
    echo -e "${YELLOW}No FQCN modules found in task files. Nothing to verify.${NC}"
    exit 0
fi

TOTAL=0
PASSED=0
FAILED=0
FAILED_LIST=""

echo -e "${CYAN}Verifying modules against installed collections...${NC}"
echo ""

while IFS= read -r module; do
    [ -z "$module" ] && continue
    TOTAL=$((TOTAL + 1))

    if ansible-doc "$module" &>/dev/null; then
        PASSED=$((PASSED + 1))
        echo -e "  ${GREEN}✓${NC} ${module}"
    else
        FAILED=$((FAILED + 1))
        FAILED_LIST+="    ${RED}✗ ${module}${NC}\n"
        echo -e "  ${RED}✗${NC} ${module} — ${RED}NOT FOUND${NC}"
    fi
done <<< "$MODULES"

echo ""
echo "───────────────────────────────────────────────────"
echo -e "  Total: ${TOTAL}  |  ${GREEN}Passed: ${PASSED}${NC}  |  ${RED}Failed: ${FAILED}${NC}"
echo "───────────────────────────────────────────────────"

if [ "$FAILED" -gt 0 ]; then
    echo ""
    echo -e "${RED}✗ FAILED: ${FAILED} module(s) do not exist!${NC}"
    echo ""
    echo "These are likely hallucinated by the AI assistant."
    echo "Fix: Run 'ansible-doc <module>' to find the correct module name,"
    echo "     or check https://docs.ansible.com/ansible/latest/collections/"
    echo ""

    # Also check for hardcoded secrets while we're here
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "  Secrets Scan (Bonus)"
    echo "═══════════════════════════════════════════════════"
    echo ""
    SECRETS=$(grep -rnEI '(password|secret|token|api_key|private_key):\s*["\x27]?[A-Za-z0-9]' \
        "${SCAN_DIRS[@]}" --include='*.yml' --include='*.yaml' 2>/dev/null \
        | grep -v 'vault' | grep -v '!vault' | grep -v '{{' | grep -v 'lookup' \
        | grep -v '#' | grep -v 'no_log' || true)
    if [ -n "$SECRETS" ]; then
        echo -e "${RED}⚠ Potential hardcoded secrets found:${NC}"
        echo "$SECRETS"
    else
        echo -e "${GREEN}✓ No hardcoded secrets detected.${NC}"
    fi

    exit 1
else
    echo ""
    echo -e "${GREEN}✓ PASSED: All ${TOTAL} modules verified as real.${NC}"
    echo ""
    exit 0
fi
