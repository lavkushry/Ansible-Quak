.PHONY: lint syntax test validate install clean fqcn-check docs setup help

help:
	@echo "Available targets:"
	@echo "  lint        - Run ansible-lint"
	@echo "  syntax      - Run syntax checks"
	@echo "  test        - Run molecule tests"
	@echo "  validate    - Run full validation suite"
	@echo "  install     - Install dependencies"
	@echo "  clean       - Clean up"
	@echo "  fqcn-check  - Check FQCN usage"
	@echo "  docs        - Generate documentation"
	@echo "  setup       - One-command project setup"

install:
	pip install -r requirements.txt
	ansible-galaxy collection install -r requirements.yml || true

setup: install
	pre-commit install

lint:
	ansible-lint

syntax:
	ansible-playbook --syntax-check playbooks/*.yml || true

test:
	molecule test

validate: lint syntax fqcn-check test

clean:
	rm -rf .tox/
	rm -rf .pytest_cache/
	rm -rf molecule/default/.molecule/
	find . -type f -name "*.retry" -delete

fqcn-check:
	@echo "Checking for missing FQCNs..."
	@bash -c "grep -r -E '^[ \t]*[a-z_]+:[ \t]*$$' playbooks/ roles/ | grep -v 'ansible.builtin' && echo 'Found non-FQCN modules!' && exit 1 || exit 0"

docs:
	@echo "Documentation generation not implemented yet."
