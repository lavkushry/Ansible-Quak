---
name: ansible-cloud-aws
description: >
  Use when automating AWS infrastructure: EC2 instances, S3 buckets, IAM,
  VPC/networking, RDS databases, Lambda, ECS/EKS, Route53, and CloudFormation.
---

# Ansible AWS Cloud Skill

This skill outlines mandatory pre-steps, complete module parameter references, common error patterns, and battle-tested examples for enterprise AWS automation.

## 1. Critical Rule
ALL AWS modules are in the `amazon.aws` collection, NEVER `ansible.builtin.aws_*`.
Ensure the `boto3` and `botocore` Python packages are installed on the controller.

## 2. Authentication Patterns
Preferred methods:
- Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- Instance profile / IAM role (When running on EC2)
- AWS CLI profile
- STS assume role

```yaml
# Authentication via environment (preferred for CI)
environment:
  AWS_ACCESS_KEY_ID: "{{ vault_aws_access_key }}"
  AWS_SECRET_ACCESS_KEY: "{{ vault_aws_secret_key }}"
  AWS_DEFAULT_REGION: "{{ aws_region }}"
```

## 3. Common AWS Modules & Complete Parameter References

- `amazon.aws.ec2_instance` — launch/manage EC2
- `amazon.aws.ec2_security_group` — security groups
- `amazon.aws.ec2_vpc_net` — VPC
- `amazon.aws.ec2_vpc_subnet` — subnets
- `amazon.aws.s3_bucket` — S3 buckets
- `amazon.aws.s3_object` — S3 objects (NOT aws_s3, that's old)
- `amazon.aws.iam_role` — IAM roles
- `amazon.aws.iam_policy` — IAM policies
- `amazon.aws.route53` — DNS records
- `amazon.aws.rds_instance` — RDS databases
- `amazon.aws.elb_application_lb` — ALB
- `amazon.aws.lambda_invoke` / `amazon.aws.lambda_event` — Lambda functions
- `amazon.aws.cloudformation` — CFN stacks

### EC2 Instance Provisioning
```yaml
- name: Provision an EC2 instance
  amazon.aws.ec2_instance:
    name: "web-server-01"
    key_name: "my_keypair"
    vpc_subnet_id: "subnet-0abcdef1234567890"
    instance_type: t3.micro
    security_group: default
    network:
      assign_public_ip: true
    image_id: ami-0abcdef1234567890
    wait: true
    wait_timeout: 300
    tags:
      Environment: Production
      Team: DevOps
    state: started
  register: ec2_info
```

### Security Group Management
```yaml
- name: Ensure security group exists
  amazon.aws.ec2_security_group:
    name: web_sg
    description: Security group for web servers
    vpc_id: vpc-12345678
    rules:
      - proto: tcp
        ports:
          - 80
          - 443
        cidr_ip: 0.0.0.0/0
      - proto: tcp
        ports:
          - 22
        cidr_ip: 10.0.0.0/8
    state: present
```

### S3 Bucket Management
```yaml
- name: Ensure S3 bucket exists
  amazon.aws.s3_bucket:
    name: my-app-data-bucket
    state: present
    tags:
      Purpose: DataStorage
```

## 4. Anti-hallucination for AWS
- `ansible.builtin.ec2` → **WRONG**, use `amazon.aws.ec2_instance`
- `ansible.builtin.aws_s3` → **WRONG**, use `amazon.aws.s3_object`
- `ansible.builtin.iam` → **WRONG**, use `amazon.aws.iam_role`
- `ec2` (bare) → **WRONG AND DEPRECATED**, use `amazon.aws.ec2_instance`
- `ec2_instance` (bare) → **WRONG**, needs FQCN
- Old module names: `ec2_ami`, `ec2_snapshot` → check amazon.aws collection for current names (e.g. `amazon.aws.ec2_ami`)

## 5. Best Practices
- Always use `wait: true` and `wait_timeout:` for async AWS operations (like creating instances or load balancers).
- Tag all resources with standard tags (Name, Environment, Team, CostCenter, etc.) using `tags:` parameter.
- Use `state: present` or `state: absent` to enforce idempotency.
- Use `register:` to capture resource IDs for downstream tasks.
- Region should be a variable (`{{ aws_region }}`), never hardcoded.
