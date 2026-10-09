.PHONY: lint syntax test validate install clean fqcn-check agent-audit setup help

help:
	@echo "Available targets:"
	@echo "  setup        - Install collections and dependencies"
	@echo "  validate     - Run full multi-stage validation suite"
	@echo "  fqcn-check   - Run AST-based FQCN anti-hallucination verification"
	@echo "  agent-audit  - Run AI Agent AST audit across all playbooks"
	@echo "  lint         - Run ansible-lint"
	@echo "  syntax       - Run syntax checks"
	@echo "  clean        - Clean temporary build and cache files"

install:
	ansible-galaxy collection install -r requirements.yml || true

setup: install
	pip install -r mcp-server/requirements.txt || true

lint:
	ansible-lint

syntax:
	ansible-playbook --syntax-check playbooks/*.yml || true

fqcn-check:
	./scripts/check-fqcn.sh

agent-audit:
	@for f in playbooks/*.yml; do python3 scripts/ansible_agent.py audit "$$f"; done

validate: fqcn-check agent-audit lint syntax

clean:
	rm -rf .tox/ .pytest_cache/ molecule/default/.molecule/
	find . -type f -name "*.retry" -delete
	find . -type f -name ".DS_Store" -delete
