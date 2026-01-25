# [WORKSPACE_NAME] - AI Workspace Context

**Organization:** [Organization Name]
**AI Assistant:** Claude (claude@[domain])
**Workspace Location:** [VPS/Server details]

> **IMPORTANT:** Always check the repo for updates before starting work. Run `git pull` and re-familiarize with any changed documentation.

## AI Assistant Role

Claude serves as the AI assistant for [Organization] with the following responsibilities:

- **[Primary Task 1]:** Description
- **[Primary Task 2]:** Description
- **[Primary Task 3]:** Description

### Email Modes

| Mode | Email | Use For |
|------|-------|---------|
| **Claude's Email** | claude@[domain] | Automated comms, follow-ups |
| **On Behalf of User** | user@[domain] | Personal responses |

**Default behavior:**
- Responding to user's inbox → use user@[domain]
- New automated communications → use claude@[domain]

### Email Tag System

All project emails use standardized subject tags:

```
[TYPE:SESSION_ID CONTEXT] Descriptive Subject
```

| Type | Meaning | Example |
|------|---------|---------|
| P | Project | `[P:P-001 Website]` |
| S | Support | `[S:S-001 Issue]` |
| I | Internal | `[I:OPS Operations]` |
| [X] | [Custom] | `[X:X-001 Context]` |

## Business Overview

[Brief description of the business and what it does]

### Key Points

- Point 1
- Point 2
- Point 3

### Team Structure (if applicable)

| Name | Role |
|------|------|
| [Name] | [Role] |

## Key Files

| File | Purpose |
|------|---------|
| `[registry].yaml` | [Entity] registry |
| `operations/session-registry.yaml` | Session management |
| `operations/memory/followups.yaml` | Scheduled tasks |
| `operations/memory/checks.yaml` | Recurring checks |

## Current Systems

| System | Purpose |
|--------|---------|
| [System 1] | [Purpose] |
| [System 2] | [Purpose] |

## Directory Structure

```
[WORKSPACE_NAME]/
├── CLAUDE.md                 # This file
├── [registry].yaml           # Primary registry
├── .mcp.json                 # MCP configuration
│
├── [entities]/               # Per-entity folders
├── operations/               # Automation & skills
│   ├── skills/
│   ├── scripts/
│   └── memory/
├── knowledge-base/           # SOPs & guides
└── infrastructure/           # Server config
```

## Available Skills

### [Category 1]

| Command | Purpose |
|---------|---------|
| `/[skill]` | [Description] |

### [Category 2]

| Command | Purpose |
|---------|---------|
| `/[skill]` | [Description] |

### Operations

| Command | Purpose |
|---------|---------|
| `/status` | Check system connectivity |
| `/email` | Draft and send emails |
| `/report` | Generate reports |

## MCP Servers

| Server | Purpose |
|--------|---------|
| **telegram** | Notifications |
| **[server]** | [Purpose] |
| **playwright** | Browser automation |
| **context7** | Documentation lookup |

## Quick Reference

```bash
# Check workspace
ls -la ~/[WORKSPACE_NAME]/

# View registry
cat ~/[WORKSPACE_NAME]/[registry].yaml

# Check session registry
cat ~/[WORKSPACE_NAME]/operations/session-registry.yaml
```

---

*Workspace initialized: [DATE]*
