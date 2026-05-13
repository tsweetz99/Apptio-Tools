# Customer Mapping Configuration Guide

Map technical VM names to business-friendly customer names for professional stakeholder reports.

## Overview

Customer mapping allows you to transform technical VM names like `vm-prod-app-01` into business-friendly names like "Customer Portal Application" in your reports. This makes reports more meaningful for non-technical stakeholders.

## Quick Start

### 1. Create Your Mapping File

```bash
# Copy the example file
cp customer_mapping.json.example customer_mapping.json
```

### 2. Edit the Mapping File

```json
{
  "vm-prod-app-01": "Customer Portal Application",
  "vm-prod-db-01": "Customer Database Server",
  "vm-dev-.*": "Development Environment"
}
```

### 3. Use with Version 3

```bash
python generate_rightsizing_report_v3.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output customer_report.xlsx
```

## Mapping File Format

The mapping file is a JSON file with key-value pairs:

```json
{
  "vm_name_or_pattern": "Customer Friendly Name",
  "another_vm": "Another Friendly Name"
}
```

### Exact Matches

Map specific VM names to friendly names:

```json
{
  "vm-prod-web-01": "Production Web Server - Customer A",
  "vm-prod-web-02": "Production Web Server - Customer B",
  "vm-prod-db-01": "Production Database - Customer A"
}
```

### Pattern Matching (Regex)

Use regular expressions to match multiple VMs:

```json
{
  "vm-prod-web-.*": "Production Web Servers",
  "vm-dev-.*": "Development Environment",
  "vm-test-.*": "Testing Environment",
  ".*-customer-a-.*": "Customer A Infrastructure",
  "db-prod-[0-9]+": "Production Database Cluster"
}
```

### Combined Approach

Mix exact matches and patterns:

```json
{
  "vm-prod-critical-01": "Critical Production Server (High Priority)",
  "vm-prod-web-.*": "Production Web Servers",
  "vm-prod-app-.*": "Production Application Servers",
  "vm-dev-.*": "Development Environment",
  "vm-uat-.*": "UAT Environment",
  ".*-customer-portal-.*": "Customer Portal Infrastructure"
}
```

## Pattern Examples

### By Environment

```json
{
  ".*-prod-.*": "Production Environment",
  ".*-dev-.*": "Development Environment",
  ".*-uat-.*": "UAT Environment",
  ".*-preprod-.*": "Pre-Production Environment"
}
```

### By Customer

```json
{
  ".*-acme-.*": "ACME Corporation",
  ".*-globex-.*": "Globex Industries",
  ".*-initech-.*": "Initech Systems"
}
```

### By Application

```json
{
  ".*-web-.*": "Web Application Servers",
  ".*-db-.*": "Database Servers",
  ".*-app-.*": "Application Servers",
  ".*-cache-.*": "Cache Servers",
  ".*-queue-.*": "Message Queue Servers"
}
```

### By Naming Convention

```json
{
  "vm-[0-9]+-prod-.*": "Production VMs",
  "vm-[0-9]+-dev-.*": "Development VMs",
  "aws-.*": "AWS Cloud Infrastructure",
  "azure-.*": "Azure Cloud Infrastructure",
  "onprem-.*": "On-Premises Infrastructure"
}
```

## Advanced Patterns

### Specific Prefixes

```json
{
  "^prod-": "Production Environment",
  "^dev-": "Development Environment",
  "^test-": "Testing Environment"
}
```

### Specific Suffixes

```json
{
  ".*-prod$": "Production Environment",
  ".*-dev$": "Development Environment",
  ".*-backup$": "Backup Servers"
}
```

### Contains Specific Text

```json
{
  ".*customer.*": "Customer-Facing Systems",
  ".*internal.*": "Internal Systems",
  ".*public.*": "Public-Facing Systems"
}
```

### Number Ranges

```json
{
  "vm-prod-[1-5][0-9]": "Production Cluster 1",
  "vm-prod-[6-9][0-9]": "Production Cluster 2",
  "vm-dev-[0-9]+": "Development VMs"
}
```

## Complete Example

Here's a comprehensive example covering multiple scenarios:

```json
{
  "vm-prod-portal-01": "Customer Portal - Primary",
  "vm-prod-portal-02": "Customer Portal - Secondary",
  "vm-prod-api-.*": "Production API Servers",
  "vm-prod-db-.*": "Production Database Cluster",
  "vm-prod-cache-.*": "Production Cache Layer",
  "vm-prod-queue-.*": "Production Message Queue",
  
  "vm-uat-.*": "UAT Environment",
  "vm-dev-.*": "Development Environment",
  "vm-test-.*": "Testing Environment",
  
  ".*-acme-.*": "ACME Corporation Infrastructure",
  ".*-globex-.*": "Globex Industries Infrastructure",
  
  "aws-prod-.*": "AWS Production Environment",
  "azure-prod-.*": "Azure Production Environment",
  "onprem-prod-.*": "On-Premises Production",
  
  "backup-.*": "Backup and DR Systems",
  "monitoring-.*": "Monitoring Infrastructure",
  "security-.*": "Security Systems"
}
```

## Best Practices

### 1. Order Matters

Place more specific patterns before general ones:

```json
{
  "vm-prod-critical-db-01": "Critical Production Database (Highest Priority)",
  "vm-prod-db-.*": "Production Database Servers",
  "vm-prod-.*": "Production Environment"
}
```

The first matching pattern wins, so specific matches should come first.

### 2. Use Descriptive Names

Make names meaningful for your audience:

```json
{
  "vm-prod-web-.*": "Customer-Facing Web Servers (Production)",
  "vm-prod-db-.*": "Production Database Cluster (24/7 Critical)"
}
```

### 3. Include Context

Add environment or priority information:

```json
{
  "vm-prod-.*": "Production Environment (Business Critical)",
  "vm-dev-.*": "Development Environment (Non-Production)",
  "vm-backup-.*": "Backup Systems (DR)"
}
```

### 4. Test Your Patterns

Test patterns before using in production:

```bash
# Test with a small subset first
python generate_rightsizing_report_v3.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --environment Dev \
    --output test_mapping.xlsx
```

### 5. Document Your Patterns

Add comments in a separate documentation file:

```
# Customer Mapping Documentation

## Pattern: vm-prod-web-.*
Matches: All production web servers
Example: vm-prod-web-01, vm-prod-web-02
Maps to: "Production Web Servers"

## Pattern: .*-acme-.*
Matches: All ACME Corporation infrastructure
Example: vm-prod-acme-app-01, db-acme-prod-01
Maps to: "ACME Corporation Infrastructure"
```

## Troubleshooting

### Pattern Not Matching

**Issue**: VMs not getting mapped despite having a pattern.

**Solution**: Check pattern syntax and test with regex tools:
```bash
# Test pattern in Python
python3 -c "import re; print(re.match('vm-prod-.*', 'vm-prod-web-01'))"
```

### Wrong Mapping Applied

**Issue**: VMs getting mapped to wrong friendly name.

**Solution**: Check pattern order. More specific patterns should come first:
```json
{
  "vm-prod-critical-01": "Critical Server",
  "vm-prod-.*": "Production Servers"
}
```

### Special Characters in VM Names

**Issue**: VM names contain special regex characters (., *, +, etc.).

**Solution**: Escape special characters:
```json
{
  "vm\\.prod\\.web\\.01": "Production Web Server 01",
  "vm-prod-\\[backup\\]": "Production Backup Server"
}
```

### Case Sensitivity

**Issue**: Patterns not matching due to case differences.

**Solution**: Use case-insensitive patterns:
```json
{
  "(?i)vm-prod-.*": "Production Servers",
  "(?i).*-customer-.*": "Customer Infrastructure"
}
```

## Validation

### Check Your Mapping File

```bash
# Validate JSON syntax
python3 -c "import json; json.load(open('customer_mapping.json'))"
```

If valid, you'll see no output. If invalid, you'll see an error message.

### Preview Mappings

Generate a test report to preview how mappings will appear:

```bash
python generate_rightsizing_report_v3.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --environment Dev \
    --output mapping_preview.xlsx
```

## Maintenance

### Regular Updates

Review and update mappings regularly:
- When new VMs are added
- When naming conventions change
- When new customers are onboarded
- When infrastructure is reorganized

### Version Control

Keep your mapping file in version control:

```bash
# Initialize git repository
git init
git add customer_mapping.json
git commit -m "Initial customer mapping configuration"

# Update and track changes
git add customer_mapping.json
git commit -m "Added mappings for new customer infrastructure"
```

### Backup

Always backup your mapping file:

```bash
# Create backup
cp customer_mapping.json customer_mapping.json.backup

# Or with timestamp
cp customer_mapping.json customer_mapping.json.$(date +%Y%m%d)
```

## Examples by Industry

### Financial Services

```json
{
  ".*-trading-.*": "Trading Platform Infrastructure",
  ".*-banking-.*": "Core Banking Systems",
  ".*-payment-.*": "Payment Processing Systems",
  ".*-compliance-.*": "Compliance and Audit Systems"
}
```

### Healthcare

```json
{
  ".*-ehr-.*": "Electronic Health Records System",
  ".*-patient-.*": "Patient Management System",
  ".*-imaging-.*": "Medical Imaging Infrastructure",
  ".*-lab-.*": "Laboratory Information System"
}
```

### E-Commerce

```json
{
  ".*-storefront-.*": "Customer Storefront",
  ".*-cart-.*": "Shopping Cart System",
  ".*-payment-.*": "Payment Gateway",
  ".*-inventory-.*": "Inventory Management System",
  ".*-shipping-.*": "Shipping and Fulfillment System"
}
```

### SaaS Platform

```json
{
  ".*-api-.*": "API Gateway and Services",
  ".*-web-.*": "Web Application Frontend",
  ".*-worker-.*": "Background Job Workers",
  ".*-analytics-.*": "Analytics and Reporting Platform",
  ".*-tenant-.*": "Multi-Tenant Infrastructure"
}
```

---

**Ready to use customer mapping?** Create your `customer_mapping.json` file and run version 3 of the report generator!