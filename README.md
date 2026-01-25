# Claude Workspace Framework

A reusable toolkit for deploying AI-assisted operational workspaces.

## Overview

This framework provides standardized packages, playbooks, and templates for building Claude-powered workspaces for any business or project.

**Live Examples:**
- **IT-Admin** - MSP operations (Systemsaholic)
- **Phoenix-Voyages** - Host travel agency

## Packages

Modular components that can be deployed independently or combined:

| Package | Description | Dependencies |
|---------|-------------|--------------|
| [session-hub](packages/session-hub/) | Session routing, registry, tmux management | - |
| [memory-system](packages/memory-system/) | Followups, checks, persistent state | - |
| [email-system](packages/email-system/) | Claude email + on-behalf-of pattern | MCP server |
| [yaml-registries](packages/yaml-registries/) | Structured data management pattern | - |
| [skills-framework](packages/skills-framework/) | Slash command system | - |
| [mcp-templates](packages/mcp-templates/) | Python MCP server boilerplate | - |
| [notification-layer](packages/notification-layer/) | Telegram alerts, escalation | MCP server |

## Playbooks

Step-by-step deployment guides:

| Playbook | Description |
|----------|-------------|
| [new-workspace](playbooks/new-workspace.md) | Bootstrap a new workspace from scratch |
| [deploy-session-hub](playbooks/deploy-session-hub.md) | Add session management to existing workspace |
| [deploy-memory-system](playbooks/deploy-memory-system.md) | Add persistent memory |
| [deploy-email-system](playbooks/deploy-email-system.md) | Set up Claude email |
| [build-mcp-server](playbooks/build-mcp-server.md) | Create a new MCP server |

## Quick Start

### 1. Scaffold a New Workspace

```bash
# Create structure
mkdir -p ~/MyWorkspace/{operations/{skills,mcp-servers,scripts,memory},knowledge-base/{sops,guides}}

# Copy templates
cp templates/CLAUDE.md ~/MyWorkspace/
cp templates/session-registry.yaml ~/MyWorkspace/operations/
```

### 2. Deploy Packages

Follow playbooks to add packages based on your needs:

```
New Workspace
    ├── Core (always)
    │   ├── CLAUDE.md context
    │   └── Folder structure
    │
    ├── Data Layer (pick what you need)
    │   ├── YAML Registries (clients, advisors, etc.)
    │   └── Entity folders
    │
    ├── Automation Layer (pick what you need)
    │   ├── Session Hub
    │   ├── Memory System
    │   └── Skills Framework
    │
    ├── Communication Layer (pick what you need)
    │   ├── Email System
    │   └── Notification Layer
    │
    └── Integration Layer (as needed)
        └── MCP Servers (custom per workspace)
```

### 3. Configure MCP Servers

Create `.mcp.json` with servers for your integrations.

## Terminology

See [GLOSSARY.md](GLOSSARY.md) for standardized terms.

## Directory Structure

```
Claude-Workspace-Framework/
├── README.md                 # This file
├── GLOSSARY.md              # Standardized terminology
│
├── packages/                # Reusable components
│   ├── session-hub/
│   ├── memory-system/
│   ├── email-system/
│   ├── yaml-registries/
│   ├── skills-framework/
│   ├── mcp-templates/
│   └── notification-layer/
│
├── playbooks/               # Deployment guides
│
├── templates/               # Skeleton files
│
└── examples/                # Reference implementations
    ├── it-admin/
    └── phoenix-voyages/
```

## Design Principles

1. **Modular** - Packages work independently
2. **File-Based** - State in YAML/markdown, not databases
3. **Git-Native** - Everything version controlled
4. **Claude-First** - Designed for AI operation
5. **Human-Readable** - Documentation as code

---

*Framework version: 1.0.0*
*Created: 2026-01-25*
