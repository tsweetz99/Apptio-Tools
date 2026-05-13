# Monthly Action Plan Report - User Guide

Generate a comprehensive monthly maintenance action plan with clear categorization for execution prioritization.

## Overview

The Monthly Action Plan report combines VM rightsizing and disk optimization recommendations into three actionable categories designed for monthly maintenance window execution:

### 1. Must-Do Actions
**Priority: IMMEDIATE**
- Policy violations (DEV/UAT Premium disks)
- Validated downsizing with high confidence
- Actions that should be executed without delay

### 2. Cost Optimization Actions
**Priority: RECOMMENDED**
- Downsizing opportunities across all environments
- Standard disk tier optimizations
- Actions that provide cost savings with acceptable risk

### 3. Reliability Investment Actions
**Priority: BUDGET APPROVAL REQUIRED**
- Production upsizing recommendations
- Performance improvements requiring additional spend
- Actions that improve reliability but increase costs

## Quick Start

### Generate Monthly Action Plan

```bash
python generate_monthly_action_plan.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID
```

This creates a file named `Monthly_Action_Plan_YYYYMMDD_HHMMSS.xlsx` with four sheets:
- **Summary** - Executive overview with totals
- **1. Must-Do Actions** - Immediate actions required
- **2. Cost Optimization** - Recommended cost savings
- **3. Reliability Investment** - Production improvements requiring budget

### With Customer Mapping

```bash
python generate_monthly_action_plan.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --customer-mapping customer_mapping.json
```

### Custom Output Filename

```bash
python generate_monthly_action_plan.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output January_2026_Action_Plan.xlsx
```

## Report Structure

### Summary Sheet

Provides executive-level overview:

| Metric | Description |
|--------|-------------|
| **Must-Do Actions** | Count and monthly savings |
| **Cost Optimization** | Count and monthly savings |
| **Reliability Investment** | Count and monthly cost increase |
| **Total Actions** | Sum of all actions |
| **Total Monthly Savings** | Combined savings from Must-Do and Cost Optimization |
| **Total Investment Required** | Cost for Reliability improvements |
| **Net Monthly Impact** | Savings minus investment |

### 1. Must-Do Actions Sheet

**Purpose**: Actions that must be executed in the maintenance window

**Includes**:
- **Policy Violations**: DEV/UAT environments using Premium SSD (should be Standard SSD)
- **Validated Downsizing**: High-confidence VM downsizing (CRITICAL/MAJOR risk severity)

**Columns**:
- Type (VM Rightsizing or Disk Tier Optimization)
- Server/Resource Name
- Customer Friendly Name
- Environment
- Action (Downsize, or Premium SSD → Standard SSD)
- Current Configuration
- Recommended Configuration
- Monthly Savings
- Justification (highlighted for policy violations)
- Risk Level
- UUID

**Visual Indicators**:
- Policy violations highlighted in red
- All actions sorted by environment and savings

### 2. Cost Optimization Actions Sheet

**Purpose**: Recommended actions for cost savings

**Includes**:
- VM downsizing across all environments (medium/low confidence)
- Disk tier optimizations in Pre-Prod/Prod/DR (require review)
- Standard cost reduction opportunities

**Columns**: Same as Must-Do Actions sheet

**Decision Criteria**:
- Review justification and risk level
- Validate with application owners
- Schedule during maintenance window
- Monitor post-implementation

### 3. Reliability Investment Actions Sheet

**Purpose**: Production improvements requiring budget approval

**Includes**:
- Production VM upsizing recommendations
- Performance improvements for overutilized resources
- Actions that increase monthly costs

**Columns**: Same as Must-Do Actions, with emphasis on:
- Net Add Cost (monthly increase)
- Justification (performance reasoning)
- Risk (typically related to performance degradation)

**Decision Criteria**:
- Requires budget approval
- Validate performance justification
- Assess business impact of current performance
- Plan capacity increase

## Use Cases

### Monthly Maintenance Window Planning

```bash
# Generate action plan
python generate_monthly_action_plan.py \
    --url https://turbo.example.com \
    --jsessionid SESSION_ID \
    --output "Maintenance_Window_$(date +%B_%Y).xlsx"

# Review output:
# 1. Execute all Must-Do Actions (policy compliance)
# 2. Select Cost Optimization actions based on capacity
# 3. Submit Reliability Investment for budget approval
```

### Quarterly Cost Review

```bash
# Generate plan for quarterly review
python generate_monthly_action_plan.py \
    --url https://turbo.example.com \
    --jsessionid SESSION_ID \
    --output "Q1_2026_Cost_Review.xlsx"

# Focus on:
# - Total Monthly Savings potential
# - Must-Do Actions for immediate wins
# - Cost Optimization trends
```

### Budget Planning

```bash
# Generate plan for budget discussions
python generate_monthly_action_plan.py \
    --url https://turbo.example.com \
    --jsessionid SESSION_ID \
    --customer-mapping customer_mapping.json \
    --output "FY2026_Budget_Plan.xlsx"

# Use Reliability Investment sheet for:
# - Capacity planning
# - Performance improvement budget
# - Infrastructure investment justification
```

## Action Categorization Logic

### Must-Do Actions

**VM Rightsizing**:
- Action Type: Downsize
- Risk Severity: CRITICAL or MAJOR
- Rationale: High confidence in underutilization

**Disk Optimization**:
- Environment: Dev or UAT
- Current Tier: Premium SSD
- Recommended Tier: Standard SSD
- Rationale: Policy violation (Premium not allowed in non-prod)

### Cost Optimization Actions

**VM Rightsizing**:
- Action Type: Downsize
- Risk Severity: MINOR or MEDIUM
- All Environments
- Rationale: Cost savings opportunity

**Disk Optimization**:
- Environment: Pre-Prod, Prod, or DR
- Any tier optimization
- Rationale: Requires review but offers savings

### Reliability Investment Actions

**VM Rightsizing**:
- Action Type: Upsize
- Environment: Prod only
- Rationale: Performance improvement requiring budget

## Understanding the Data

### Monthly Savings Calculation

```
Monthly Savings = Hourly Cost Reduction × 730 hours
```

Based on Turbonomic's cost statistics for downsizing actions.

### Net Add Cost Calculation

```
Net Add Cost = Hourly Cost Increase × 730 hours
```

For upsizing actions in Production environment only.

### Policy Compliance

**DEV/UAT Disk Policy**:
- **Allowed**: Standard SSD, Standard HDD
- **Not Allowed**: Premium SSD, Ultra SSD
- **Rationale**: Non-production workloads don't require premium performance

**Production Disk Policy**:
- **Allowed**: All tiers
- **Requirement**: Review and approval for changes
- **Rationale**: Production performance must be validated

## Execution Workflow

### Phase 1: Must-Do Actions (Week 1)

1. **Review Must-Do Actions sheet**
   - Identify policy violations (highlighted in red)
   - Validate downsizing recommendations

2. **Notify Stakeholders**
   - Alert application owners
   - Schedule maintenance window
   - Prepare rollback plan

3. **Execute Actions**
   - Start with policy violations
   - Proceed with validated downsizing
   - Monitor post-change

4. **Document Results**
   - Track actual savings
   - Note any issues
   - Update runbook

### Phase 2: Cost Optimization (Week 2-3)

1. **Review Cost Optimization sheet**
   - Prioritize by savings amount
   - Assess risk levels
   - Validate with app owners

2. **Select Actions**
   - Choose based on capacity
   - Consider business impact
   - Plan testing approach

3. **Execute Selected Actions**
   - Implement in batches
   - Monitor performance
   - Measure savings

4. **Report Results**
   - Calculate actual savings
   - Document lessons learned
   - Update for next month

### Phase 3: Reliability Investment (Week 4)

1. **Review Reliability Investment sheet**
   - Assess performance justification
   - Calculate budget impact
   - Prioritize by business criticality

2. **Budget Approval**
   - Present to management
   - Justify performance needs
   - Get approval for spend

3. **Plan Implementation**
   - Schedule with app owners
   - Plan capacity increase
   - Prepare monitoring

4. **Execute Approved Actions**
   - Implement upsizing
   - Validate performance improvement
   - Confirm cost increase

## Best Practices

### 1. Regular Generation

Generate monthly action plans on a consistent schedule:

```bash
# First Monday of each month
0 9 1 * 1 /path/to/generate_monthly_action_plan.sh
```

### 2. Stakeholder Communication

- Share Summary sheet with executives
- Share Must-Do Actions with operations team
- Share Reliability Investment with budget owners
- Share Cost Optimization with application teams

### 3. Track Execution

Maintain a tracking spreadsheet:

| Month | Must-Do Executed | Cost Opt Executed | Reliability Executed | Actual Savings | Actual Investment |
|-------|------------------|-------------------|---------------------|----------------|-------------------|
| Jan   | 15/15            | 8/12              | 2/3                 | $12,450        | $3,200            |

### 4. Continuous Improvement

- Review execution success rate
- Adjust categorization thresholds
- Refine customer mapping
- Update policies based on results

### 5. Documentation

Keep records of:
- Monthly action plans
- Execution results
- Stakeholder approvals
- Lessons learned

## Troubleshooting

### No Must-Do Actions

**Possible Causes**:
- No policy violations found
- No high-confidence downsizing opportunities
- Filters too restrictive

**Solution**: Review Cost Optimization sheet for opportunities

### High Reliability Investment Costs

**Possible Causes**:
- Production environment underprovisioned
- Workload growth
- Performance degradation

**Solution**: 
- Validate performance metrics
- Assess business impact
- Prioritize critical applications

### Actions Not Appearing

**Possible Causes**:
- No pending recommendations in Turbonomic
- Session ID expired
- Environment tags missing

**Solution**:
```bash
# Get fresh session ID
curl -X POST 'https://turbo.example.com/api/v3/login' \
     -d 'username=admin&password=pass' -c cookies.txt

# Regenerate report
python generate_monthly_action_plan.py \
    --url https://turbo.example.com \
    --jsessionid $(grep JSESSIONID cookies.txt | awk '{print $7}')
```

### Customer Names Not Mapping

**Possible Causes**:
- Customer mapping file not found
- VM names don't match patterns
- Mapping file has errors

**Solution**:
```bash
# Verify mapping file exists
ls -l customer_mapping.json

# Test mapping file syntax
python -c "import json; json.load(open('customer_mapping.json'))"

# Regenerate with mapping
python generate_monthly_action_plan.py \
    --url https://turbo.example.com \
    --jsessionid SESSION_ID \
    --customer-mapping customer_mapping.json
```

## Integration Examples

### Email Automation

```bash
#!/bin/bash
# monthly_action_plan_email.sh

# Generate report
python generate_monthly_action_plan.py \
    --url https://turbo.example.com \
    --jsessionid $SESSION_ID \
    --output "Monthly_Action_Plan_$(date +%Y%m).xlsx"

# Email to stakeholders
mail -s "Monthly Action Plan - $(date +%B %Y)" \
     -a "Monthly_Action_Plan_$(date +%Y%m).xlsx" \
     stakeholders@company.com < email_body.txt
```

### Slack Notification

```python
import requests

# After generating report
webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
message = {
    "text": f"Monthly Action Plan generated: {total_actions} actions, ${total_savings:,.2f} potential savings"
}
requests.post(webhook_url, json=message)
```

### JIRA Ticket Creation

```python
from jira import JIRA

# Create tickets for Must-Do Actions
jira = JIRA(server='https://jira.company.com', basic_auth=('user', 'pass'))

for action in must_do_actions:
    jira.create_issue(
        project='OPS',
        summary=f"Must-Do: {action['Server/Resource Name']}",
        description=action['Justification'],
        issuetype={'name': 'Task'}
    )
```

## Advanced Usage

### Custom Categorization

Modify the categorization logic in the script:

```python
# In generate_action_plan() method
# Adjust thresholds for Must-Do Actions
if risk_severity in ['CRITICAL', 'MAJOR', 'HIGH']:  # Add 'HIGH'
    must_do_actions.append(action_data)
```

### Additional Filters

Add environment-specific filters:

```python
# Only include specific environments
if environment not in ['Prod', 'Pre-Prod']:
    continue
```

### Custom Metrics

Add custom columns to the report:

```python
action_data = {
    # ... existing fields ...
    'Business Unit': get_business_unit(vm_name),
    'Cost Center': get_cost_center(vm_name),
    'Priority': calculate_priority(action)
}
```

## Support

For issues or questions:
1. Check this documentation
2. Review [INSTALLATION.md](INSTALLATION.md) for setup issues
3. See [CUSTOMER_MAPPING.md](CUSTOMER_MAPPING.md) for mapping configuration
4. Verify Turbonomic credentials and permissions

## Related Documentation

- [README.md](README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [CUSTOMER_MAPPING.md](CUSTOMER_MAPPING.md) - Customer mapping guide
- [INSTALLATION.md](INSTALLATION.md) - Installation instructions

---

**Ready to create your first Monthly Action Plan?** Run the quick start command and review the Summary sheet!