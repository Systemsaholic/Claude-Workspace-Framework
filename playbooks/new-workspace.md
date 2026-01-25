# Playbook: Create New Workspace

Step-by-step guide to bootstrap a new Claude workspace from scratch.

## Prerequisites

- [ ] VPS or server with SSH access
- [ ] Claude Code installed on target
- [ ] Domain/email access (for Claude email)
- [ ] Telegram bot (for notifications)

## Phase 1: Foundation

### 1.1 Create Folder Structure

```bash
# SSH to target server
ssh user@server

# Create workspace root
mkdir -p ~/WorkspaceName

# Create core folders
mkdir -p ~/WorkspaceName/{operations/{skills,mcp-servers,scripts,memory},knowledge-base/{sops,guides,templates}}

# Create data folders (customize per business)
mkdir -p ~/WorkspaceName/{clients,projects}  # OR
mkdir -p ~/WorkspaceName/{advisors,suppliers}  # OR
mkdir -p ~/WorkspaceName/{customers,products}
```

### 1.2 Create CLAUDE.md

Create the main context document:

```markdown
# [Business Name] - AI Workspace Context

**Organization:** [Business Name]
**AI Assistant:** Claude (claude@domain.com)
**Workspace Location:** [VPS details]

## AI Assistant Role

Claude serves as the AI assistant with responsibilities:
- [List primary tasks]
- [List primary tasks]
- [List primary tasks]

## Business Overview

[Brief description of the business]

## Key Files

| File | Purpose |
|------|---------|
| `[registry].yaml` | [Description] |

## Current Systems

| System | Purpose |
|--------|---------|
| [System] | [Purpose] |

## Directory Structure

[Show folder structure]

## Available Skills

| Command | Purpose |
|---------|---------|
| `/[skill]` | [Purpose] |
```

### 1.3 Create .mcp.json

Start with base MCP servers:

```json
{
  "mcpServers": {
    "telegram": {
      "command": "path/to/telegram-mcp",
      "env": {
        "TELEGRAM_BOT_TOKEN": "your-token",
        "TELEGRAM_CHAT_ID": "your-chat-id"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp", "--headless"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

## Phase 2: Data Layer

### 2.1 Design Registry Schema

Determine what entities you need to track:

| Business Type | Primary Registry | Secondary |
|---------------|------------------|-----------|
| MSP | `clients.yaml` | `servers.yaml` |
| Travel Agency | `advisors.yaml` | `suppliers.yaml` |
| Consultancy | `clients.yaml` | `projects.yaml` |
| E-commerce | `products.yaml` | `customers.yaml` |

### 2.2 Create Registry Template

```yaml
# [entities].yaml

[entities]:
  EXAMPLE:
    name: "Example Entity"
    email: "email@example.com"
    status: active
    # Add fields relevant to your business

stats:
  total_active: 0
  last_updated: "YYYY-MM-DD"
```

### 2.3 Create Entity Folders

```bash
mkdir -p ~/WorkspaceName/[entities]/{ENTITY-CODE}
```

## Phase 3: Session Management

### 3.1 Define Session Types

Choose prefixes relevant to your business:

| Prefix | Category | Example |
|--------|----------|---------|
| I | Internal | I-OPS (always) |
| P | Project | P-001 |
| C | Client | C-ACME |
| [X] | [Custom] | [Example] |

### 3.2 Create Session Registry

```yaml
# operations/session-registry.yaml

sessions:
  I-OPS:
    name: Operations Hub
    category: internal
    status: active
    created: "YYYY-MM-DDTHH:MM:SSZ"

counters:
  I: 1
  P: 0
  # Add your prefixes

routing_rules:
  keywords: []
  domains: {}

snooze:
  emails: {}
  tasks: {}
```

## Phase 4: Memory System

### 4.1 Create Memory Files

```bash
mkdir -p ~/WorkspaceName/operations/memory

echo "followups: []" > ~/WorkspaceName/operations/memory/followups.yaml
echo "checks: []" > ~/WorkspaceName/operations/memory/checks.yaml
```

### 4.2 Set Up Cron (Optional)

```bash
# Copy memory-cron.sh to operations/scripts/
# Add to crontab:
crontab -e
# * * * * * /path/to/operations/scripts/memory-cron.sh
```

## Phase 5: Communication

### 5.1 Create Claude Email Account

In cPanel/email provider:
1. Create `claude@yourdomain.com`
2. Note IMAP/SMTP settings
3. Generate app password if needed

### 5.2 Configure Email MCP

Add to `.mcp.json`:

```json
"workspace-email": {
  "command": "path/to/email-mcp",
  "env": {
    "EMAIL_ADDRESS": "claude@yourdomain.com",
    "EMAIL_PASSWORD": "password",
    "IMAP_HOST": "mail.yourdomain.com",
    "SMTP_HOST": "mail.yourdomain.com"
  }
}
```

### 5.3 Set Up Telegram Notifications

1. Create Telegram group/channel for this workspace
2. Get chat ID
3. Update `.mcp.json` with new chat ID

## Phase 6: Skills

### 6.1 Create Skills Folder

```bash
mkdir -p ~/WorkspaceName/operations/skills
```

### 6.2 Create Core Skills

**Minimum skills for any workspace:**

```markdown
# /status skill
Check status of all connected systems.

# /email skill
Draft and send emails.

# /report skill
Generate reports.
```

### 6.3 Create Business-Specific Skills

Add skills relevant to your use case.

## Phase 7: Verification

### 7.1 Test Checklist

- [ ] Can SSH/mosh to workspace
- [ ] CLAUDE.md loads correctly
- [ ] MCP servers connect
- [ ] Can send Telegram notification
- [ ] Can send email (if configured)
- [ ] Registry files parse correctly
- [ ] Skills execute correctly

### 7.2 First Run

```bash
cd ~/WorkspaceName
claude

# Test basic operations
/status
```

## Post-Deployment

### Git Setup (Recommended)

```bash
cd ~/WorkspaceName
git init
git add .
git commit -m "Initial workspace setup"
git remote add origin git@github.com:org/workspace.git
git push -u origin main
```

### Documentation

- [ ] Update CLAUDE.md with any changes
- [ ] Document MCP server configurations
- [ ] Create SOPs for common tasks
- [ ] Document skills and their usage

---

## Quick Reference

### Minimum Viable Workspace

```
WorkspaceName/
├── CLAUDE.md           # Required
├── .mcp.json           # Required (at least telegram)
└── operations/
    └── session-registry.yaml
```

### Recommended Workspace

```
WorkspaceName/
├── CLAUDE.md
├── .mcp.json
├── [entities].yaml
├── [entities]/
├── operations/
│   ├── skills/
│   ├── scripts/
│   ├── memory/
│   │   ├── followups.yaml
│   │   └── checks.yaml
│   └── session-registry.yaml
└── knowledge-base/
    ├── sops/
    └── guides/
```

---

*Playbook version: 1.0.0*
