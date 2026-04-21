# Summary Report Example

This document shows what the **Summary_Report.txt** file will contain.

## Report Format

The Summary Report is a formatted text file that matches the terminal output style for easy readability.

## Example Output

```
================================================================================
COMPREHENSIVE REPORT SUMMARY
================================================================================
Total Recommendations: 6283
  - Downsizing: 4999
  - Upsizing: 1106
  - Other: 178

Estimated Monthly Savings: $243,791.93
Estimated Monthly Add Cost: $19,083.24
Net Monthly Impact: $224,708.68

Environment Breakdown:
  - Dev: 952
  - Pre-Prod: 6
  - Prod: 2011
  - UAT: 188
  - Unmapped: 3126
================================================================================

================================================================================
DEV ENVIRONMENT SUMMARY
================================================================================
Total Recommendations: 952
  - Downsizing: 624
  - Upsizing: 328
  - Other: 0

Estimated Monthly Savings: $17,597.76
Estimated Monthly Add Cost: $0.00
Net Monthly Impact: $17,597.76

Environment Breakdown:
  - Dev: 952
================================================================================

================================================================================
PRE-PROD ENVIRONMENT SUMMARY
================================================================================
Total Recommendations: 6
  - Downsizing: 6
  - Upsizing: 0
  - Other: 0

Estimated Monthly Savings: $336.25
Estimated Monthly Add Cost: $0.00
Net Monthly Impact: $336.25

Environment Breakdown:
  - Pre-Prod: 6
================================================================================

================================================================================
PROD ENVIRONMENT SUMMARY
================================================================================
Total Recommendations: 2011
  - Downsizing: 1741
  - Upsizing: 270
  - Other: 0

Estimated Monthly Savings: $175,025.65
Estimated Monthly Add Cost: $19,083.24
Net Monthly Impact: $155,942.40

Environment Breakdown:
  - Prod: 2011
================================================================================

================================================================================
UAT ENVIRONMENT SUMMARY
================================================================================
Total Recommendations: 188
  - Downsizing: 142
  - Upsizing: 46
  - Other: 0

Estimated Monthly Savings: $11,386.83
Estimated Monthly Add Cost: $0.00
Net Monthly Impact: $11,386.83

Environment Breakdown:
  - UAT: 188
================================================================================

================================================================================
UNMAPPED ENVIRONMENT SUMMARY
================================================================================
Total Recommendations: 3126
  - Downsizing: 2486
  - Upsizing: 462
  - Other: 178

Estimated Monthly Savings: $39,445.44
Estimated Monthly Add Cost: $0.00
Net Monthly Impact: $39,445.44

Environment Breakdown:
  - Unmapped: 3126
================================================================================
```

## Use Cases

### Executive Presentations
- Quick overview of optimization opportunities
- Clear financial impact summary
- Environment-level breakdown for prioritization

### Budget Planning
- Monthly cost reduction estimates
- Investment requirements (upsizing costs)
- Net financial impact for forecasting

### Environment Analysis
- Compare optimization opportunities across environments
- Identify which environments have the most potential savings
- Track environment-specific metrics

## File Format

The report is exported as a plain text file:
- **Text format**: `Summary_Report_TIMESTAMP.txt`

This format is:
- Easy to read in any text editor
- Simple to copy/paste into emails or documents
- Compatible with version control systems
- No Excel or special software required

## Example Output

When you run the script, you'll see:

```
Generating summary report...
  ✓ Summary report exported to: reports/Summary_Report_20260421_123456.txt
```

The text file will be created in the same directory as your other reports and can be opened with any text editor.