# AWS Credentials Setup Guide

## Overview

The `get_redshift_nodes.py` script uses boto3 (AWS SDK for Python) which requires AWS credentials to authenticate API calls. You need an **AWS Access Key ID** and **AWS Secret Access Key**, NOT a password.

## What You Need

1. **AWS Access Key ID** - Example: `AKIAIOSFODNN7EXAMPLE`
2. **AWS Secret Access Key** - Example: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
3. **IAM Permissions** - Your AWS user/role needs `redshift:DescribeClusters` permission

## Setup Methods (Choose One)

### Method 1: AWS CLI Configuration (Recommended)

This is the easiest and most secure method.

#### Step 1: Install AWS CLI

```bash
# macOS
brew install awscli

# Or using pip
pip install awscli
```

#### Step 2: Configure AWS CLI

```bash
aws configure
```

You'll be prompted for:
```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

This creates `~/.aws/credentials` and `~/.aws/config` files that boto3 will automatically use.

#### Step 3: Verify Configuration

```bash
# Test AWS credentials
aws sts get-caller-identity

# Test Redshift access
aws redshift describe-clusters
```

### Method 2: Environment Variables

Set AWS credentials as environment variables:

```bash
# In your terminal or add to ~/.bashrc or ~/.zshrc
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export AWS_DEFAULT_REGION="us-east-1"

# Then run the script
python cloudability/get_redshift_nodes.py
```

### Method 3: Credentials File (Manual)

Create credentials file manually:

```bash
# Create AWS directory
mkdir -p ~/.aws

# Create credentials file
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
EOF

# Create config file
cat > ~/.aws/config << EOF
[default]
region = us-east-1
output = json
EOF
```

### Method 4: IAM Role (For EC2/Lambda)

If running on AWS infrastructure (EC2, Lambda, ECS, etc.), attach an IAM role with appropriate permissions. No credentials needed in code.

## Getting AWS Access Keys

### If You Have AWS Console Access:

1. Log into AWS Console
2. Go to **IAM** → **Users** → Select your user
3. Click **Security credentials** tab
4. Click **Create access key**
5. Choose **Command Line Interface (CLI)**
6. Download or copy the Access Key ID and Secret Access Key
7. **Important**: Save the Secret Access Key immediately - you can't retrieve it later!

### If You Don't Have Access Keys:

Contact your AWS administrator to:
1. Create an IAM user for you
2. Generate access keys
3. Attach a policy with `redshift:DescribeClusters` permission

## Required IAM Permissions

Your AWS user/role needs this IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "redshift:DescribeClusters",
        "ec2:DescribeRegions"
      ],
      "Resource": "*"
    }
  ]
}
```

### Minimal Read-Only Policy

For security, use the AWS managed policy: `AmazonRedshiftReadOnlyAccess`

Or create a custom policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "redshift:Describe*",
        "redshift:List*",
        "ec2:DescribeRegions"
      ],
      "Resource": "*"
    }
  ]
}
```

## Troubleshooting

### Issue: "Unable to locate credentials"

**Solution**: AWS credentials are not configured. Use Method 1 (AWS CLI) above.

```bash
aws configure
```

### Issue: "An error occurred (UnauthorizedOperation)"

**Solution**: Your AWS user lacks necessary permissions. Contact your AWS admin to add `redshift:DescribeClusters` permission.

### Issue: Password prompt appears

**Cause**: This happens when credentials are not properly configured and boto3 tries to use other authentication methods.

**Solution**: 
1. Check if `~/.aws/credentials` exists and has valid credentials
2. Run `aws configure` to set up credentials properly
3. Verify with: `aws sts get-caller-identity`

### Issue: "The security token included in the request is expired"

**Solution**: Your temporary credentials have expired. If using AWS SSO or temporary credentials, re-authenticate:

```bash
aws sso login
# or
aws sts get-session-token
```

### Issue: "Access Denied" for specific regions

**Solution**: Some regions may be disabled in your AWS account. Use `--region` flag to specify an enabled region:

```bash
python cloudability/get_redshift_nodes.py --region us-east-1
```

## Testing Your Setup

After configuring credentials, test with these commands:

```bash
# 1. Verify AWS identity
aws sts get-caller-identity

# 2. Test Redshift access
aws redshift describe-clusters --region us-east-1

# 3. Run the Python script
python cloudability/get_redshift_nodes.py --region us-east-1
```

## Security Best Practices

1. **Never commit credentials to Git**
   - Add `~/.aws/credentials` to `.gitignore`
   - Use environment variables or AWS Secrets Manager for CI/CD

2. **Use IAM roles when possible**
   - For EC2: Attach IAM role to instance
   - For Lambda: Use execution role
   - For local development: Use AWS SSO

3. **Rotate access keys regularly**
   - AWS recommends rotating keys every 90 days
   - Use `aws iam create-access-key` to create new keys

4. **Use least privilege**
   - Only grant `redshift:DescribeClusters` permission
   - Avoid using admin or power user credentials

5. **Enable MFA for IAM users**
   - Adds extra security layer
   - Required for sensitive operations

## Alternative: Using AWS SSO

If your organization uses AWS SSO:

```bash
# Configure SSO
aws configure sso

# Login
aws sso login --profile your-profile-name

# Use with script
AWS_PROFILE=your-profile-name python cloudability/get_redshift_nodes.py
```

## Quick Start Summary

```bash
# 1. Install AWS CLI
brew install awscli  # or: pip install awscli

# 2. Configure credentials
aws configure
# Enter your Access Key ID and Secret Access Key

# 3. Test
aws redshift describe-clusters

# 4. Run the script
python cloudability/get_redshift_nodes.py
```

## Additional Resources

- [AWS CLI Configuration Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [AWS Credentials Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Boto3 Credentials Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
- [IAM Policies for Redshift](https://docs.aws.amazon.com/redshift/latest/mgmt/redshift-iam-authentication-access-control.html)