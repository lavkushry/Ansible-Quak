# Ansible MCP Server

This MCP server wraps `ansible-doc` to provide accurate module documentation to AI agents, helping prevent hallucinations when writing Ansible playbooks.

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

This server is designed to be run as an MCP server. It provides the following tools:
- `get_module_doc(module_fqcn)`
- `list_modules(collection)`
- `get_module_params(module_fqcn)`
- `validate_module_exists(module_fqcn)`
- `search_modules(keyword)`
