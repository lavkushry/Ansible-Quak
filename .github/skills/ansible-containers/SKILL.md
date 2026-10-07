---
name: ansible-containers
description: >
  Use when managing Docker containers, Docker Compose stacks, container images,
  Docker networks/volumes, or Kubernetes resources via Ansible.
---

# Ansible Containers Skill

This skill outlines mandatory pre-steps, complete module parameter references, common error patterns, and battle-tested examples for enterprise container and Kubernetes automation.

## Mandatory Pre-Steps
1. Ensure the correct collections are installed: `community.docker` and `kubernetes.core`.
2. Ensure required Python libraries for the modules are installed (e.g., `docker` or `docker-compose` python packages depending on the module).

## 1. Docker Management (community.docker)

**Critical Rule**: ALL Docker modules are in `community.docker`, NOT `ansible.builtin`.

- `community.docker.docker_container` — run/manage containers
- `community.docker.docker_image` — build/pull/push images
- `community.docker.docker_network` — manage networks
- `community.docker.docker_volume` — manage volumes
- `community.docker.docker_compose_v2` — manage compose stacks (NOT `docker_compose`, that's deprecated)
- `community.docker.docker_login` — registry authentication
- `community.docker.docker_prune` — cleanup

### Managing Containers
```yaml
- name: Run a Nginx container
  community.docker.docker_container:
    name: my_nginx
    image: nginx:latest
    state: started
    restart_policy: always
    ports:
      - "8080:80"
    volumes:
      - /path/to/html:/usr/share/nginx/html:ro
    env:
      NGINX_HOST: foobar.com
      NGINX_PORT: 80
  become: true
```

### Managing Compose Stacks
```yaml
- name: Deploy Docker Compose stack
  community.docker.docker_compose_v2:
    project_src: /opt/my_project
    state: present
    pull: always
    recreate: auto
  become: true
```

## 2. Docker Installation via Ansible

The RIGHT way — never use snap or distro package. Always use the official Docker repository.

```yaml
- name: Install Docker prerequisites
  ansible.builtin.apt:
    name:
      - apt-transport-https
      - ca-certificates
      - curl
      - gnupg
      - lsb-release
    state: present
  become: true

- name: Add Docker GPG key
  ansible.builtin.apt_key:
    url: https://download.docker.com/linux/ubuntu/gpg
    state: present
  become: true

- name: Add Docker repository
  ansible.builtin.apt_repository:
    repo: "deb https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
    state: present
  become: true

- name: Install Docker Engine
  ansible.builtin.apt:
    name:
      - docker-ce
      - docker-ce-cli
      - containerd.io
      - docker-buildx-plugin
      - docker-compose-plugin
    state: present
    update_cache: true
  become: true

- name: Ensure Docker is started and enabled
  ansible.builtin.service:
    name: docker
    state: started
    enabled: true
  become: true
```

## 3. Kubernetes Management (kubernetes.core)

**Critical Rule**: ALL Kubernetes modules are in `kubernetes.core`, NOT `ansible.builtin`.

- `kubernetes.core.k8s` — manage any K8s resource
- `kubernetes.core.helm` — manage Helm charts
- `kubernetes.core.k8s_info` — query K8s resources
- `kubernetes.core.k8s_exec` — execute in pods
- `kubernetes.core.k8s_log` — get pod logs

### Managing K8s Resources
```yaml
- name: Create a namespace
  kubernetes.core.k8s:
    name: my-namespace
    api_version: v1
    kind: Namespace
    state: present

- name: Deploy an application from a template
  kubernetes.core.k8s:
    state: present
    definition: "{{ lookup('ansible.builtin.template', 'deployment.yml.j2') }}"
```

### Managing Helm Charts
```yaml
- name: Deploy ingress-nginx helm chart
  kubernetes.core.helm:
    name: ingress-nginx
    chart_ref: ingress-nginx/ingress-nginx
    release_namespace: ingress-nginx
    create_namespace: true
    values:
      controller:
        metrics:
          enabled: true
```

## 4. Anti-hallucination & Error Patterns
- `docker_container` is NOT in `ansible.builtin`. Use `community.docker.docker_container`.
- `docker_compose` is DEPRECATED. Use `community.docker.docker_compose_v2`.
- `k8s` is NOT in `ansible.builtin`. Use `kubernetes.core.k8s`.
- Missing python libraries: Make sure `docker` python module is installed via `ansible.builtin.pip` for docker modules, and `kubernetes` for k8s modules.
