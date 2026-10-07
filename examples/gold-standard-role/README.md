# Webserver Role

A gold-standard Ansible role demonstrating best practices for configuring a webserver.

## Role Variables
- `webserver_port`: Port to listen on (default: 80)
- `webserver_packages`: List of packages to install

## Example Playbook
```yaml
- hosts: webservers
  roles:
     - role: webserver
```
