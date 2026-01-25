# /contribute-framework

Push improvements made to the framework back to the upstream repository.

## Purpose

When you make improvements to framework code (packages, playbooks, templates) in your deployed workspace, this skill helps you contribute those improvements back to the main framework repository so other workspaces can benefit.

## Usage

```
/contribute-framework
/contribute-framework "Description of the improvement"
```

## Workflow

1. **Detect Changes** - Identify modified files in `framework/` directory
2. **Validate Purity** - Run validation to ensure no project-specific content
3. **Review Changes** - Show diff of what will be contributed
4. **Confirm & Push** - Get approval and push to upstream

## Pre-flight Checks

Before contributing, the skill verifies:

- [ ] Changes are only in `framework/` directory
- [ ] No API keys, tokens, or credentials
- [ ] No real email addresses (only @example.com placeholders)
- [ ] No hardcoded IPs (only test ranges)
- [ ] No project-specific paths or names
- [ ] No sensitive files (.env, .pem, etc.)

## Implementation

When this skill is invoked:

### Step 1: Check for Framework Changes

```bash
# Check if framework remote exists
git remote get-url framework || echo "Framework remote not configured"

# Show changes in framework directory
git status framework/
git diff --stat framework/
```

### Step 2: Run Purity Validator

```bash
# Run the framework validator
./framework/scripts/validate-framework.sh ./framework

# If validation fails, STOP and report issues
# User must fix issues before contributing
```

### Step 3: Show Changes for Review

```bash
# Show detailed diff of changes
git diff framework/

# List affected files
git diff --name-only framework/
```

### Step 4: Confirm and Push

After user confirms:

```bash
# Stage framework changes only
git add framework/

# Commit with descriptive message
git commit -m "Improve framework: [description]

[Detailed explanation of the improvement]

Contributed from: [workspace-name]

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to upstream framework
git subtree push --prefix=framework framework main
```

## Example Session

```
User: /contribute-framework "Add file locking to memory system"

Claude: Let me check for framework changes...

📁 Modified files in framework/:
  - framework/packages/memory-system/README.md
  - framework/packages/memory-system/locking.md (new)

🔍 Running purity validation...
  ✓ No API keys or tokens
  ✓ No real email addresses
  ✓ No hardcoded IPs
  ✓ No project-specific paths
  ✓ Framework is clean

📝 Changes to contribute:

  packages/memory-system/README.md
  + Added locking mechanism documentation
  + New section on preventing race conditions

  packages/memory-system/locking.md (new file)
  + File locking implementation guide
  + Examples for followups.yaml and checks.yaml

Would you like me to push these improvements to the framework repository?

User: Yes

Claude: ✓ Committed: "Improve framework: Add file locking to memory system"
✓ Pushed to framework repository

Other workspaces can now pull this improvement with:
  ./framework/scripts/framework-sync.sh pull
```

## Troubleshooting

### "Framework remote not configured"

```bash
git remote add framework https://github.com/YOUR_ORG/Claude-Workspace-Framework.git
```

### Validation Fails

Fix the reported issues before contributing:
- Replace real emails with @example.com
- Remove any API keys or credentials
- Use placeholder names instead of real ones
- Check FRAMEWORK-RULES.md for guidelines

### Push Rejected

Pull latest changes first:
```bash
./framework/scripts/framework-sync.sh pull
# Resolve any conflicts
/contribute-framework
```

## What NOT to Contribute

- Project-specific configurations
- Custom skills for your organization
- Registry data (clients, advisors, etc.)
- MCP server configs with real credentials
- Anything in `workspace/` directory

## What TO Contribute

- Bug fixes in framework packages
- New features that benefit all workspaces
- Documentation improvements
- New templates (with placeholder values)
- Playbook updates
- Validation script improvements
