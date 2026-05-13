# Disk Optimization Report Generator

Generate Azure disk tier optimization reports with policy enforcement for DEV/UAT environments.

## Overview

This tool generates reports focused on Azure disk storage tier optimizations with built-in policy enforcement:

- **DEV & UAT**: Policy requires Standard SSD only (Premium SSD = violation)
- **Pre-Prod, Prod, DR**: Recommendations provided for review

## Quick Start

```bash
cd turbonomic/rightsizing-report

# Basic usage
python3 generate_disk_optimization_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output-dir disk_reports/

# With customer mapping
python3 generate_disk_optimization_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --customer-mapping customer_mapping.json \
    --output-dir disk_reports/
```

## Report Columns

| Column | Description |
|--------|-------------|
| **Environment** | DEV, UAT, Pre-Prod, Prod, DR, or Unmapped |
| **Server Name** | VM the disk is attached to |
| **Disk Name** | Storage identifier |
| **Current Tier** | Current disk tier (Premium SSD, Standard SSD, etc.) |
| **Recommended Tier** | Turbonomic recommended tier |
| **Policy Compliance** | Compliance status based on environment policy |
| **Monthly Savings** | Estimated cost reduction per disk |
| **Actionable** | Whether action can be taken immediately |
| **Turbonomic Link** | Direct link to action details in Turbonomic UI |
| **Customer ID** | Customer identifier from tags |
| **Customer Friendly Name** | Mapped customer name |
| **Business Account** | Azure subscription/account name |
| **Cloud Provider** | Azure, AWS, GCP |
| **Action State** | READY, QUEUED, etc. |
| **Risk** | Risk severity |
| **Details** | Action description |
| **UUID** | Unique identifier |

## Policy Enforcement

### DEV & UAT Environments

**Policy**: Standard SSD only - Premium SSD not allowed

- **Policy Compliance**: "VIOLATION - Premium SSD not allowed" if Premium SSD detected
- **Actionable**: "Yes - Policy Violation" for immediate action
- **Priority**: High - immediate cost savings opportunity

**Example:**
```
Environment: Dev
Current Tier: Premium SSD
Recommended Tier: Standard SSD
Policy Compliance: VIOLATION - Premium SSD not allowed
Actionable: Yes - Policy Violation
Monthly Savings: $45.50
```

### Pre-Prod, Prod, DR Environments

**Policy**: Recommendations require performance validation

- **Policy Compliance**: "Review Required"
- **Actionable**: "Review Required"
- **Priority**: Lower - case-by-case basis

**Example:**
```
Environment: Prod
Current Tier: Premium SSD
Recommended Tier: Standard SSD
Policy Compliance: Review Required
Actionable: Review Required
Monthly Savings: $125.00
```

## Generated Reports

The script creates 8 reports:

1. **Disk_Optimization_Report_TIMESTAMP.xlsx** - All disk recommendations
2. **Dev_Disk_Optimization_TIMESTAMP.xlsx** - DEV environment only
3. **UAT_Disk_Optimization_TIMESTAMP.xlsx** - UAT environment only
4. **Pre-Prod_Disk_Optimization_TIMESTAMP.xlsx** - Pre-Prod environment only
5. **Prod_Disk_Optimization_TIMESTAMP.xlsx** - Prod environment only
6. **DR_Disk_Optimization_TIMESTAMP.xlsx** - DR environment only
7. **Unmapped_Disk_Optimization_TIMESTAMP.xlsx** - Unmapped resources

## Command Options

```bash
python3 generate_disk_optimization_report.py \
    --url <TURBO_URL> \
    --jsessionid <SESSION_ID> \
    [OPTIONS]
```

### Required Arguments

- `--url` - Turbonomic instance URL
- `--jsessionid` - Session ID from login

### Optional Arguments

- `--output-dir <DIR>` - Output directory (default: current directory)
- `--format <FORMAT>` - Output format: `excel` (default) or `csv`
- `--all-clouds` - Include all cloud providers (not just Azure)
- `--customer-mapping <FILE>` - Path to customer ID to name mapping JSON file

## Usage Examples

### Example 1: Basic Usage

```bash
python3 generate_disk_optimization_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output-dir ./disk_reports
```

### Example 2: With Customer Mapping

```bash
python3 generate_disk_optimization_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --customer-mapping customer_mapping.json \
    --output-dir ./disk_reports
```

### Example 3: CSV Format

```bash
python3 generate_disk_optimization_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --format csv \
    --output-dir ./disk_reports
```

### Example 4: All Cloud Providers

```bash
python3 generate_disk_optimization_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --all-clouds \
    --output-dir ./disk_reports
```

## Console Output Example

```
Fetching storage actions from https://your-turbo-instance.com/api/v3/markets/Market/actions...
  Retrieved 500 actions (total: 500)
  Retrieved 234 actions (total: 734)
Total storage actions retrieved: 734

Generating disk optimization report...
  ✓ Exported 156 records to: disk_reports/Disk_Optimization_Report_20260421_123456.xlsx

================================================================================
COMPREHENSIVE DISK OPTIMIZATION SUMMARY
================================================================================
Total Disk Recommendations: 156
  - Policy Violations (DEV/UAT Premium SSD): 45
  - Immediately Actionable: 45
  - Review Required: 111

Estimated Monthly Savings: $12,450.50
  - From Policy Violations: $3,250.00

Environment Breakdown:
  - Dev: 28 disks ($1,850.00 savings)
    └─ 28 policy violations
  - UAT: 17 disks ($1,400.00 savings)
    └─ 17 policy violations
  - Prod: 89 disks ($7,800.50 savings)
  - Pre-Prod: 12 disks ($950.00 savings)
  - DR: 10 disks ($450.00 savings)
================================================================================

Generating environment-specific reports...
  ✓ Exported 28 records to: disk_reports/Dev_Disk_Optimization_20260421_123456.xlsx

================================================================================
DEV DISK OPTIMIZATION SUMMARY
================================================================================
Total Disk Recommendations: 28
  - Policy Violations (DEV/UAT Premium SSD): 28
  - Immediately Actionable: 28
  - Review Required: 0

Estimated Monthly Savings: $1,850.00
  - From Policy Violations: $1,850.00

Environment Breakdown:
  - Dev: 28 disks ($1,850.00 savings)
    └─ 28 policy violations
================================================================================

✓ All reports generated in: disk_reports/
```

## Workflow Recommendations

### For DEV/UAT Policy Violations

1. **Review the report** - Focus on "Policy Compliance" = "VIOLATION"
2. **Validate savings** - Check "Monthly Savings" column
3. **Take immediate action** - All violations are immediately actionable
4. **Track progress** - Monitor reduction in violations over time

### For Prod/Pre-Prod/DR Recommendations

1. **Review recommendations** - Check "Actionable" = "Review Required"
2. **Assess performance impact** - Validate with application teams
3. **Test in lower environments** - Verify performance with Standard SSD
4. **Implement gradually** - Start with non-critical workloads

## Disk Tier Information

### Azure Disk Tiers

| Tier | Use Case | Performance | Cost |
|------|----------|-------------|------|
| **Premium SSD** | Production workloads | High IOPS/throughput | Highest |
| **Standard SSD** | Web servers, dev/test | Moderate IOPS | Medium |
| **Standard HDD** | Backup, non-critical | Low IOPS | Lowest |
| **Ultra SSD** | Mission-critical | Highest IOPS | Very High |

### Policy Rationale

**DEV/UAT Standard SSD Policy:**
- Development and testing workloads typically don't require Premium SSD performance
- Standard SSD provides sufficient performance for most dev/test scenarios
- Significant cost savings without impacting development velocity
- Premium SSD should be exception-based with business justification

## Troubleshooting

### Issue: No storage actions found

If you're getting no results, see the comprehensive troubleshooting guide:

**[DISK_OPTIMIZATION_TROUBLESHOOTING.md](DISK_OPTIMIZATION_TROUBLESHOOTING.md)**

This guide includes:
- Step-by-step diagnostic process
- Debug script to identify the issue
- Common causes and solutions
- Alternative query approaches
- Turbonomic configuration checks

**Quick Debug:**
```bash
# Run the storage discovery debug script
python3 debug_storage_entities.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID
```

### Issue: All disks show "Review Required"

**Solution:**
- Check environment detection logic
- Verify BusinessAccount names or environment tags are set correctly
- Review the Unmapped report for miscategorized resources

### Issue: Savings calculations seem incorrect

**Solution:**
- Verify Turbonomic has accurate Azure pricing data
- Check that cost stats are available in the API response
- Review the action details for cost information

## Integration with Existing Tools

This tool uses the same:
- Customer mapping file as the rightsizing report
- Environment detection logic
- Authentication method (JSESSIONID)
- Output format options

You can use the same `customer_mapping.json` file for both tools.

## Best Practices

1. **Run regularly** - Weekly or monthly to track policy compliance
2. **Focus on violations first** - Address DEV/UAT Premium SSD usage
3. **Document exceptions** - Track approved Premium SSD usage in DEV/UAT
4. **Validate before action** - Test tier changes in non-production first
5. **Monitor performance** - Track application performance after tier changes

## Support

For issues or questions:
- See [USAGE_V3.md](USAGE_V3.md) for general Turbonomic reporting
- See [CUSTOMER_MAPPING_README.md](CUSTOMER_MAPPING_README.md) for customer mapping
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for installation help