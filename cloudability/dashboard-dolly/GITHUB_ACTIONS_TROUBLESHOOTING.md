# GitHub Actions Troubleshooting

## Workflow Not Appearing in Actions Tab

If you don't see "Build Dashboard Dolly Executables" in the Actions tab, try these solutions:

### Solution 1: Check if Actions is Enabled

1. Go to your GitHub repository
2. Click **Settings** tab
3. Click **Actions** → **General** (left sidebar)
4. Under "Actions permissions", ensure one of these is selected:
   - ✅ "Allow all actions and reusable workflows"
   - ✅ "Allow [organization] actions and reusable workflows"
5. Click **Save** if you made changes
6. Refresh the Actions tab

### Solution 2: Verify File Location and Name

The workflow file MUST be at exactly this path:
```
.github/workflows/build-dashboard-dolly.yml
```

Check:
```bash
# Verify the file exists
ls -la .github/workflows/build-dashboard-dolly.yml

# Should show the file with correct path
```

If the file is missing or in wrong location:
```bash
# Create the directory if needed
mkdir -p .github/workflows

# Verify it was created in the right place
ls -la .github/workflows/
```

### Solution 3: Check File Was Actually Pushed

```bash
# Check git status
git status

# Check if file is tracked
git ls-files .github/workflows/build-dashboard-dolly.yml

# If it returns nothing, the file wasn't added. Add it:
git add .github/workflows/build-dashboard-dolly.yml
git commit -m "Add GitHub Actions workflow"
git push origin main
```

### Solution 4: Check Branch

Workflows only appear if they're on the **default branch** (usually `main` or `master`).

```bash
# Check current branch
git branch

# Check default branch on GitHub
# Go to repo → Settings → General → Default branch

# If you're on wrong branch, switch to default:
git checkout main
git push origin main
```

### Solution 5: Wait and Refresh

Sometimes GitHub takes a few minutes to process new workflows:

1. Wait 2-3 minutes after pushing
2. Hard refresh the Actions page (Ctrl+F5 or Cmd+Shift+R)
3. Try a different browser or incognito mode

### Solution 6: Check for YAML Syntax Errors

```bash
# Check if the YAML is valid
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/build-dashboard-dolly.yml'))"

# If there's an error, it will show the line number
```

### Solution 7: Repository Type Issues

**Private Repository:**
- Actions might be disabled by organization policy
- Check with your GitHub admin

**Forked Repository:**
- Workflows are disabled by default in forks
- Go to Actions tab → Click "I understand..." button

### Solution 8: Manual Trigger Test

Even if the workflow doesn't show in the sidebar, you can try triggering it:

1. Go to Actions tab
2. Look for any workflows listed
3. If you see the workflow name anywhere, click it
4. Look for "Run workflow" button

## Quick Diagnostic Commands

Run these to check your setup:

```bash
# 1. Verify file exists and location
find . -name "build-dashboard-dolly.yml" -type f

# 2. Check file contents (first few lines)
head -10 .github/workflows/build-dashboard-dolly.yml

# 3. Verify it's committed and pushed
git log --oneline -5 | grep -i workflow

# 4. Check current branch
git branch --show-current

# 5. Check remote status
git status
```

## Alternative: Create Workflow via GitHub UI

If the file approach isn't working:

1. Go to your GitHub repository
2. Click **Actions** tab
3. Click **"New workflow"**
4. Click **"set up a workflow yourself"**
5. Replace the default content with our workflow
6. Click **"Start commit"** → **"Commit new file"**

## Test with Simple Workflow

Create a minimal test workflow to verify Actions work:

```yaml
# .github/workflows/test.yml
name: Test Workflow
on:
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test
        run: echo "GitHub Actions is working!"
```

If this appears and works, then the issue is with our specific workflow file.

## Still Not Working?

If none of these solutions work:

1. **Check GitHub Status**: Visit https://www.githubstatus.com/
2. **Try Different Browser**: Clear cache or use incognito
3. **Check Organization Settings**: Your org might restrict Actions
4. **Contact GitHub Support**: If it's a platform issue

## What Should You See?

When working correctly, you should see:

1. **Actions Tab**: Shows "Build Dashboard Dolly Executables"
2. **Workflow List**: Shows in left sidebar
3. **Run Workflow Button**: Available when you click the workflow
4. **Recent Runs**: Shows any previous executions

## Next Steps

Once you can see the workflow:

1. Click **"Build Dashboard Dolly Executables"**
2. Click **"Run workflow"**
3. Select branch (usually `main`)
4. Click **"Run workflow"** button
5. Wait for build to complete (~10 minutes)
6. Download artifacts from completed run

Let me know which solution worked for you!