# Framework Management Playbook

How to use the Claude Workspace Framework as a reusable template across multiple deployments.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  GitHub: Claude-Workspace-Framework (Template Repo)         │
│  ├── packages/        ← Framework core (reusable)           │
│  ├── playbooks/       ← Deployment guides                   │
│  ├── templates/       ← Skeleton files                      │
│  ├── scripts/         ← Helper scripts                      │
│  └── examples/        ← Reference implementations           │
└─────────────────────────────────────────────────────────────┘
                           ▲
              git subtree push (improvements)
              git subtree pull (updates)
                           │
┌─────────────────────────────────────────────────────────────┐
│  Deployed Workspace (e.g., Support VPS)                     │
│  ├── framework/       ← Subtree of template repo            │
│  │   ├── packages/                                          │
│  │   ├── playbooks/                                         │
│  │   ├── templates/                                         │
│  │   └── scripts/                                           │
│  ├── workspace/       ← PROJECT-SPECIFIC                    │
│  │   ├── CLAUDE.md                                          │
│  │   ├── registries/  (clients.yaml, etc.)                  │
│  │   ├── skills/                                            │
│  │   └── memory/      (followups.yaml, checks.yaml)         │
│  └── mcp-servers/     ← PROJECT-SPECIFIC MCPs               │
└─────────────────────────────────────────────────────────────┘
```

## Key Concepts

| Term | Description |
|------|-------------|
| **Framework** | The reusable packages, playbooks, and templates (this repo) |
| **Workspace** | A deployed instance with project-specific configuration |
| **Subtree** | Git feature that embeds one repo inside another |
| **Upstream** | The main framework repo on GitHub |

## Creating a New Workspace

### Step 1: Create Project Repository

```bash
mkdir my-workspace && cd my-workspace
git init
```

### Step 2: Add Framework as Subtree

```bash
# Add framework remote
git remote add framework https://github.com/YOUR_ORG/Claude-Workspace-Framework.git

# Pull framework as subtree
git subtree add --prefix=framework framework main --squash
```

### Step 3: Create Project Structure

```bash
# Create workspace directories
mkdir -p workspace/{registries,skills,memory}
mkdir -p mcp-servers

# Copy templates
cp framework/templates/CLAUDE.md workspace/
cp framework/templates/checks.yaml workspace/memory/
cp framework/templates/followups.yaml workspace/memory/
cp framework/templates/registry.yaml workspace/registries/entities.yaml
```

### Step 4: Configure Workspace

Edit `workspace/CLAUDE.md` with your project-specific context:
- Organization details
- Session types
- Entity registries
- Available skills
- MCP server configurations

## Syncing Framework Updates

When improvements are made to the framework (e.g., new features, bug fixes):

### Pull Updates

```bash
# Using the helper script
./framework/scripts/framework-sync.sh pull

# Or manually
git fetch framework
git subtree pull --prefix=framework framework main --squash
```

### Check Status

```bash
./framework/scripts/framework-sync.sh status
```

## Contributing Improvements Back

When you make improvements to framework code (in `framework/packages/`, etc.):

### Step 1: Commit Your Changes

```bash
# Make your changes in framework/packages/memory-system/...
git add framework/
git commit -m "Add locking mechanism to memory system"
```

### Step 2: Push to Upstream

```bash
# Using helper script
./framework/scripts/framework-sync.sh push

# Or manually
git subtree push --prefix=framework framework main
```

### Step 3: Pull on Other Deployments

On your other workspaces:
```bash
./framework/scripts/framework-sync.sh pull
```

## Directory Separation Rules

### Framework Code (DO push upstream)
- `framework/packages/*` - Core framework packages
- `framework/playbooks/*` - Deployment guides
- `framework/templates/*` - Skeleton files
- `framework/scripts/*` - Helper scripts
- `framework/examples/*` - Reference implementations

### Project Code (DO NOT push upstream)
- `workspace/*` - All project-specific config
- `mcp-servers/*` - Custom MCP implementations
- Root-level project files

## Best Practices

### 1. Keep Framework Generic
When improving framework code, ensure changes work for any deployment:
- No hardcoded organization names
- No project-specific paths
- Use configuration over constants

### 2. Document Changes
Update relevant README files when changing framework packages.

### 3. Test Before Pushing
Verify improvements work in your deployment before pushing upstream.

### 4. Use Meaningful Commits
```bash
# Good
git commit -m "Add file locking to memory system to prevent race conditions"

# Bad
git commit -m "Update"
```

### 5. Pull Before Push
Always pull latest changes before pushing to avoid conflicts:
```bash
./framework/scripts/framework-sync.sh pull
# resolve any conflicts
./framework/scripts/framework-sync.sh push
```

## Troubleshooting

### "Remote 'framework' not found"
```bash
git remote add framework https://github.com/YOUR_ORG/Claude-Workspace-Framework.git
```

### Merge Conflicts
When pulling updates with local changes:
1. Stash or commit your local changes first
2. Pull the update
3. Resolve conflicts manually
4. Commit the merge

### Subtree Split Issues
If push fails with split errors:
```bash
# Force a fresh split
git subtree split --prefix=framework -b framework-split
git push framework framework-split:main
git branch -D framework-split
```

## Environment Variables

The `framework-sync.sh` script supports:

| Variable | Default | Description |
|----------|---------|-------------|
| `FRAMEWORK_REMOTE` | `framework` | Git remote name |
| `FRAMEWORK_PREFIX` | `framework` | Subtree directory |
| `FRAMEWORK_BRANCH` | `main` | Branch to sync |
| `FRAMEWORK_URL` | - | URL for init command |
