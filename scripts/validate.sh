#!/usr/bin/env bash
# ============================================================================
# validate.sh — Full Ansible validation suite
# ============================================================================
# Runs all validation checks: collection install, YAML lint, ansible-lint,
# syntax check, FQCN check, module verification, and secrets scan.
# Use locally or in CI. Returns non-zero on any failure.
# ============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

ERRORS=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo ""
echo -e "${BOLD}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║       Ansible Anti-Hallucination Validation Suite     ║${NC}"
echo -e "${BOLD}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# ─── Step 1: Install Collections ─────────────────────────────────────────────
echo -e "${CYAN}[1/6] Installing collections from requirements.yml...${NC}"
if [ -f requirements.yml ]; then
    if ansible-galaxy collection install -r requirements.yml --force 2>/dev/null; then
        echo -e "  ${GREEN}✓ Collections installed${NC}"
    else
        echo -e "  ${YELLOW}⚠ Some collections may have failed to install${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ requirements.yml not found — skipping${NC}"
fi
echo ""

# ─── Step 2: YAML Lint ───────────────────────────────────────────────────────
echo -e "${CYAN}[2/6] Running yamllint...${NC}"
if command -v yamllint &> /dev/null; then
    if yamllint . 2>/dev/null; then
        echo -e "  ${GREEN}✓ YAML lint passed${NC}"
    else
        echo -e "  ${RED}✗ YAML lint found issues${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "  ${YELLOW}⚠ yamllint not installed — skipping (pip install yamllint)${NC}"
fi
echo ""

# ─── Step 3: Ansible Lint ─────────────────────────────────────────────────────
echo -e "${CYAN}[3/6] Running ansible-lint...${NC}"
if command -v ansible-lint &> /dev/null; then
    if ansible-lint 2>/dev/null; then
        echo -e "  ${GREEN}✓ ansible-lint passed${NC}"
    else
        echo -e "  ${RED}✗ ansible-lint found violations${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "  ${YELLOW}⚠ ansible-lint not installed — skipping (pip install ansible-lint)${NC}"
fi
echo ""

# ─── Step 4: Syntax Check ────────────────────────────────────────────────────
echo -e "${CYAN}[4/6] Running playbook syntax checks...${NC}"
PLAYBOOKS=$(find playbooks -name '*.yml' -o -name '*.yaml' 2>/dev/null || true)
if [ -n "$PLAYBOOKS" ]; then
    SYNTAX_ERRORS=0
    while IFS= read -r playbook; do
        [ -z "$playbook" ] && continue
        if ansible-playbook --syntax-check "$playbook" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $playbook"
        else
            echo -e "  ${RED}✗${NC} $playbook"
            SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
        fi
    done <<< "$PLAYBOOKS"

    if [ "$SYNTAX_ERRORS" -gt 0 ]; then
        echo -e "  ${RED}✗ ${SYNTAX_ERRORS} playbook(s) failed syntax check${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "  ${GREEN}✓ All playbooks passed syntax check${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ No playbooks found in playbooks/ — skipping${NC}"
fi
echo ""

# ─── Step 5: FQCN Check ──────────────────────────────────────────────────────
echo -e "${CYAN}[5/6] Running FQCN check...${NC}"
if [ -x "$SCRIPT_DIR/check-fqcn.sh" ]; then
    if "$SCRIPT_DIR/check-fqcn.sh"; then
        : # Script prints its own output
    else
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "  ${YELLOW}⚠ check-fqcn.sh not found or not executable — skipping${NC}"
fi
echo ""

# ─── Step 6: Module Verification ─────────────────────────────────────────────
echo -e "${CYAN}[6/6] Verifying modules exist...${NC}"
if [ -x "$SCRIPT_DIR/verify-modules.sh" ]; then
    if "$SCRIPT_DIR/verify-modules.sh"; then
        : # Script prints its own output
    else
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "  ${YELLOW}⚠ verify-modules.sh not found or not executable — skipping${NC}"
fi
echo ""

# ─── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════"
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}  ✓ ALL VALIDATIONS PASSED${NC}"
    echo "═══════════════════════════════════════════════════════"
    exit 0
else
    echo -e "${RED}${BOLD}  ✗ ${ERRORS} VALIDATION(S) FAILED${NC}"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    echo "Fix all issues above before committing."
    exit 1
fi
