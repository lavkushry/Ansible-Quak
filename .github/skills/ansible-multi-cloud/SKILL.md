---
name: ansible-multi-cloud
description: >
  MANDATORY skill for multi-cloud automation across AWS (amazon.aws), Azure (azure.azcollection),
  and Google Cloud Platform (google.cloud). Enforces correct collections, FQCNs, and authentication.
---

# Multi-Cloud Automation Skill (`amazon.aws`, `azure.azcollection`, `google.cloud`)

## Core Rule: Use Cloud-Specific Collections

Never use legacy bare modules (`ec2`, `azure_rm`, `gce`). Always use the official collection FQCN:
- **AWS**: `amazon.aws.*` (or `community.aws.*`)
- **Microsoft Azure**: `azure.azcollection.*`
- **Google Cloud Platform**: `google.cloud.*`

```yaml
# In requirements.yml
collections:
  - name: amazon.aws
    version: ">=7.4.0"
  - name: azure.azcollection
    version: ">=2.0.0"
  - name: google.cloud
    version: ">=1.3.0"
```

---

## 1. Authentication Standards Across Clouds

Always run cloud control-plane tasks with `delegate_to: localhost`.

### AWS Authentication
Use IAM roles / instance profiles, or pass credentials via environment/Vault:
```yaml
environment:
  AWS_ACCESS_KEY_ID: "{{ vault_aws_access_key }}"
  AWS_SECRET_ACCESS_KEY: "{{ vault_aws_secret_key }}"
  AWS_DEFAULT_REGION: "{{ aws_region | default('us-east-1') }}"
```

### Azure Authentication
Use Service Principal credentials or Managed Identity:
```yaml
environment:
  AZURE_CLIENT_ID: "{{ vault_azure_client_id }}"
  AZURE_SECRET: "{{ vault_azure_client_secret }}"
  AZURE_SUBSCRIPTION_ID: "{{ vault_azure_subscription_id }}"
  AZURE_TENANT: "{{ vault_azure_tenant_id }}"
```

### Google Cloud (GCP) Authentication
Use Service Account JSON file path or ADC:
```yaml
environment:
  GCP_SERVICE_ACCOUNT_FILE: "{{ gcp_sa_key_file }}"
  GCP_PROJECT: "{{ gcp_project_id }}"
```

---

## 2. Amazon Web Services (AWS) Patterns

### Pattern A: EC2 Instance Deployment
```yaml
- name: Launch EC2 Instance in Private Subnet
  amazon.aws.ec2_instance:
    name: "web-prod-{{ item }}"
    image_id: "ami-0c55b159cbfafe1f0"
    instance_type: "t3.medium"
    key_name: "prod-deployer-key"
    vpc_subnet_id: "{{ private_subnet_id }}"
    security_group: "{{ web_security_group_id }}"
    network:
      assign_public_ip: false
    tags:
      Environment: "Production"
      Owner: "DevOps"
      ManagedBy: "Ansible"
    wait: true
    state: running
  loop: [1, 2]
  delegate_to: localhost
  tags: ['aws', 'ec2']
```

### Pattern B: Route53 DNS Management
```yaml
- name: Ensure Public DNS Record points to CDN / Load Balancer
  amazon.aws.route53:
    state: present
    zone: "example.com"
    record: "app.example.com"
    type: CNAME
    ttl: 300
    value: "app-prod-alb-123456.us-east-1.elb.amazonaws.com"
    overwrite: true
  delegate_to: localhost
  tags: ['aws', 'dns']
```

---

## 3. Microsoft Azure Patterns

### Pattern A: Virtual Network & Subnet Provisioning
```yaml
- name: Create Azure Virtual Network
  azure.azcollection.azure_rm_virtualnetwork:
    resource_group: "rg-production-networking"
    name: "vnet-prod-eastus"
    address_prefixes_cidr:
      - "10.50.0.0/16"
    subnets:
      - name: "snet-web"
        address_prefix_cidr: "10.50.10.0/24"
      - name: "snet-database"
        address_prefix_cidr: "10.50.20.0/24"
  delegate_to: localhost
  tags: ['azure', 'network']
```

### Pattern B: Azure Linux Virtual Machine
```yaml
- name: Create Azure Linux Virtual Machine
  azure.azcollection.azure_rm_virtualmachine:
    resource_group: "rg-production-compute"
    name: "vm-app-01"
    vm_size: "Standard_D2s_v5"
    admin_username: "azureuser"
    ssh_password_enabled: false
    ssh_public_keys:
      - path: "/home/azureuser/.ssh/authorized_keys"
        key_data: "{{ vault_ssh_public_key }}"
    image:
      offer: "0001-com-ubuntu-server-jammy"
      publisher: "Canonical"
      sku: "22_04-lts-gen2"
      version: "latest"
  delegate_to: localhost
  tags: ['azure', 'vm']
```

---

## 4. Google Cloud Platform (GCP) Patterns

### Pattern A: Compute Engine Instance
```yaml
- name: Create GCP Compute Engine Instance
  google.cloud.gcp_compute_instance:
    name: "gcp-app-node-01"
    machine_type: "n2-standard-2"
    zone: "us-central1-a"
    project: "{{ gcp_project_id }}"
    auth_kind: "serviceaccount"
    service_account_file: "{{ gcp_sa_key_file }}"
    disks:
      - auto_delete: true
        boot: true
        initialize_params:
          source_image: "projects/ubuntu-os-cloud/global/images/family/ubuntu-2204-lts"
    network_interfaces:
      - network:
          selfLink: "global/networks/vpc-prod"
        subnetwork:
          selfLink: "regions/us-central1/subnetworks/subnet-apps"
    state: present
  delegate_to: localhost
  tags: ['gcp', 'compute']
```

---

## 5. Multi-Cloud Anti-Hallucination Matrix

| Provider | Hallucinated / Deprecated Name | Correct Real Collection & FQCN |
|---|---|---|
| **AWS** | `ec2` or `ec2_instance` | ✅ `amazon.aws.ec2_instance` |
| **AWS** | `s3_bucket` (bare) | ✅ `amazon.aws.s3_bucket` |
| **AWS** | `aws_s3` | ✅ `amazon.aws.s3_object` |
| **AWS** | `route53` (bare) | ✅ `amazon.aws.route53` |
| **Azure**| `azure_rm_virtualmachine` (bare)| ✅ `azure.azcollection.azure_rm_virtualmachine` |
| **Azure**| `azure_rm_vnet` | ✅ `azure.azcollection.azure_rm_virtualnetwork` |
| **GCP**  | `gce_instance` | ✅ `google.cloud.gcp_compute_instance` |
| **GCP**  | `gcp_compute` | ✅ `google.cloud.gcp_compute_instance` |
| **All**  | `ansible.builtin.ec2 / s3 / etc.` | ❌ Cloud modules are NEVER in `ansible.builtin` |

---

## 6. Pre-Flight Checklist
- [ ] Always run with `delegate_to: localhost`.
- [ ] Store API keys, Client Secrets, and Service Account files in Ansible Vault.
- [ ] Never hardcode IP addresses or cloud regions into task definitions — use variables.
- [ ] Ensure wait conditions (`wait: true`) are set for async cloud resource provisioning.
