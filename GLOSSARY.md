# Claude Workspace Framework - Glossary

Standardized terminology for AI workspace development.

---

## Core Concepts

### Workspace
A complete AI-assisted operational environment for a business or project. Contains all configuration, data, automation, and documentation needed for Claude to operate autonomously.

**Examples:** IT-Admin (Acme MSP), Phoenix-Voyages (Horizon Travel)

### Package
A reusable, self-contained component that provides specific functionality. Packages can be deployed independently or combined to build a complete workspace.

**Examples:** Session Hub, Memory System, Email System

### Playbook
Step-by-step instructions for deploying a package or performing a complex operation. Playbooks are executable documentation.

### Skill
A slash command (`/command`) that triggers a specific workflow or capability. Skills are defined in markdown files and executed by Claude.

**Examples:** `/client`, `/email`, `/status`, `/advisor`

### MCP Server
Model Context Protocol server - a service that exposes tools/APIs to Claude. MCP servers bridge Claude to external systems.

**Examples:** telegram-mcp, groundhogg-mcp, email-mcp

---

## Session Management

### Session
A persistent Claude conversation context, typically running in a tmux window. Sessions maintain state across interactions.

### Session ID
Unique identifier for a session using the format `PREFIX-NUMBER` or `PREFIX-CODE`.

**Format:** `[TYPE]-[ID]`
- `P-001` - Project session
- `I-OPS` - Internal operations
- `A-SMITH` - Advisor-specific session

### Session Type Prefix
Single letter indicating session category:

| Prefix | Category | Use Case |
|--------|----------|----------|
| P | Project | Time-bound work with deliverables |
| S | Support | Ongoing support/tickets |
| I | Internal | Infrastructure, operations |
| A | Advisor/Agent | Person-specific sessions |
| R | Recruitment | Pipeline/prospect sessions |
| M | Marketing | Campaigns, content |
| C | Client | Client-specific work |
| K | (Custom) | Client-code prefix |

### Session Registry
YAML file (`session-registry.yaml`) that tracks all sessions, routing rules, and state.

### Session Hub
The complete session management system including registry, routing logic, and tmux integration.

---

## Memory System

### Memory
Persistent storage that survives across Claude sessions. File-based state management.

### Followup
A one-time scheduled task that triggers at a specific time. Stored in `followups.yaml`.

### Check
A recurring scheduled task (daily, weekly, etc.). Stored in `checks.yaml`.

### Memory Cron
Background process that monitors memory files and triggers due items.

---

## Email System

### Claude's Email
Dedicated email account for Claude's automated communications (e.g., `claude@domain.com`).

### On-Behalf-Of Email
User's email account that Claude can send from when responding as the user.

### Email Tag
Standardized subject prefix for routing and tracking: `[TYPE:SESSION_ID CONTEXT]`

**Example:** `[P:K-001 Kenworth-Web] Website Update Status`

### Email Mode
The identity Claude uses when sending email:
- **Claude Mode** - From Claude's own address
- **Proxy Mode** - On behalf of user

---

## Data Structures

### Registry (YAML)
Central source of truth for a data type. Single file containing all records.

**Examples:**
- `clients.yaml` - All clients
- `advisors.yaml` - All advisors
- `suppliers.yaml` - All suppliers

### Entity Folder
Per-record folder containing detailed documentation and assets.

```
clients/
├── {client-code}/
│   ├── profile.md
│   ├── projects/
│   └── notes/
```

### Entity Code
Short identifier for a record, typically uppercase.

**Patterns:**
- `SMITH` - Name-based (first initial + last)
- `RCCL` - Abbreviation
- `lapierre` - Kebab-case slug

---

## Automation

### n8n Workflow
Visual automation flow in n8n. Triggers Claude sessions or performs background tasks.

### Runbook Script
Shell script that wraps Claude invocation for specific tasks.

**Example:** `triage-ticket.sh`, `health-report.sh`

### Skill File
Markdown file defining a slash command. Located in `skills/` or `.claude/commands/`.

---

## Infrastructure

### VPS
Virtual Private Server hosting the workspace. Runs Claude Code, MCP servers, and automation.

### Tailscale
Mesh VPN for secure access to workspace servers.

### tmux
Terminal multiplexer for persistent CLI sessions.

### Mosh
Mobile shell - SSH replacement with better connection resilience.

---

## Notifications

### Telegram Alert
Notification sent via Telegram bot for urgent items or decisions.

### Escalation
Routing an item to a human when Claude can't handle it autonomously.

### Snooze
Temporarily deferring an item for later processing.

---

## Workspace Lifecycle

### Scaffold
Create initial folder structure and skeleton files for a new workspace.

### Deploy
Install and configure a package in a workspace.

### Bootstrap
Initial setup of a workspace including all core packages.

### Sync
Update workspace from external systems (pull data into YAML registries).

---

*Last updated: 2026-01-25*
