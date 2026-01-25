# Session Hub Package

Manages Claude sessions, routing, and persistent context across conversations.

## Overview

The Session Hub provides:
- **Session Registry** - Track all active/inactive sessions
- **Routing Logic** - Direct emails/tasks to correct sessions
- **Email Tags** - Standardized subject tagging for tracking
- **tmux Integration** - Persistent terminal sessions
- **Counters** - Auto-increment session IDs

## Components

```
session-hub/
├── session-registry.yaml    # Main registry file
├── routing-rules.md         # Routing logic documentation
├── email-tags.md           # Tag format specification
└── scripts/
    ├── session-manager.sh   # Session lifecycle
    ├── route-email.sh       # Email routing
    └── memory-cron.sh       # Scheduled task handler
```

## Session Registry Structure

```yaml
# session-registry.yaml

sessions:
  I-OPS:
    name: Operations Hub
    category: internal
    status: active
    created: "2026-01-25T00:00:00Z"
    last_activity: "2026-01-25T00:00:00Z"
    tmux_session: I-OPS
    special: operations_hub
    description: |
      Main operations session.
    keywords:
      - operations
      - general

  P-001:
    name: Website Redesign
    category: project
    client: acme
    status: active
    created: "2026-01-20T00:00:00Z"
    project_folder: clients/acme/projects/2026-01-website
    keywords:
      - website
      - redesign
    participants:
      - client@acme.com

counters:
  P: 1   # Projects
  S: 0   # Support
  I: 1   # Internal
  # Add more as needed

client_prefixes:
  acme: A
  kenworth: K

email_tags:
  P:P-001:
    type: project
    session_id: P-001
    context: Website
    thread_ids: []

routing_rules:
  keywords:
    - pattern: "(urgent|emergency)"
      priority: high
      action: alert_telegram
    - pattern: "(invoice|billing)"
      category: internal
  domains:
    acme.com: A

snooze:
  emails: {}
  tasks: {}

investigations: {}
```

## Session Types

| Prefix | Category | Use Case | Example |
|--------|----------|----------|---------|
| P | Project | Time-bound deliverables | P-001 |
| S | Support | Ongoing tickets/issues | S-042 |
| I | Internal | Infrastructure, ops | I-OPS |
| C | Client | Client-specific | C-ACME |
| A | Advisor | Person-specific | A-SMITH |
| R | Recruitment | Pipeline prospects | R-001 |
| M | Marketing | Campaigns | M-001 |

## Email Tag Format

```
[TYPE:SESSION_ID CONTEXT] Subject Line
```

**Examples:**
- `[P:P-001 Website] Design mockups ready`
- `[S:S-042 Login-Bug] Fix deployed`
- `[I:OPS] Daily health report`

## Routing Logic

### Tier 1: Rule-Based (Fast)
1. Check subject for existing tag → route to session
2. Check sender in known participants → route to their session
3. Check domain in routing rules → route by domain
4. Check keywords → apply category/priority

### Tier 2: AI Classification (If Tier 1 low confidence)
1. Load email + registry context
2. Claude scores routing confidence
3. If >= 85% → auto-route
4. If < 85% → escalate to Telegram for human decision

## Deployment

### Prerequisites
- tmux installed
- Telegram MCP (for escalation)
- n8n (optional, for email triggers)

### Steps

1. **Create registry file**
   ```bash
   mkdir -p operations
   cp templates/session-registry.yaml operations/
   ```

2. **Configure initial sessions**
   ```yaml
   # At minimum, create I-OPS
   sessions:
     I-OPS:
       name: Operations Hub
       category: internal
       status: active
   ```

3. **Set up counters**
   ```yaml
   counters:
     P: 0
     S: 0
     I: 1
   ```

4. **Add routing rules** (optional)
   ```yaml
   routing_rules:
     keywords:
       - pattern: "(urgent)"
         priority: high
     domains:
       clientdomain.com: C
   ```

5. **Deploy scripts** (for automated routing)
   ```bash
   cp scripts/session-manager.sh operations/scripts/
   chmod +x operations/scripts/*.sh
   ```

## Usage

### Create New Session
```yaml
# Add to sessions:
P-002:
  name: New Project
  category: project
  client: acme
  status: active
  created: "2026-01-25T10:00:00Z"

# Increment counter
counters:
  P: 2
```

### Tag an Email
When sending project email:
```
Subject: [P:P-002 NewProject] Kickoff meeting scheduled
```

### Route Incoming Email
1. Parse subject for tag
2. If tag found → route to session
3. If no tag → apply routing rules
4. If uncertain → escalate

### Close Session
```yaml
P-002:
  status: completed
  completed_at: "2026-01-30T16:00:00Z"
```

## Integration Points

| System | Integration |
|--------|-------------|
| **n8n** | Webhook triggers for incoming email |
| **Telegram** | Escalation for uncertain routing |
| **tmux** | Persistent session terminals |
| **Memory System** | Followups routed to sessions |

## Files

| File | Purpose |
|------|---------|
| `session-registry.yaml` | Main state file |
| `session-manager.sh` | Create/close sessions |
| `route-email.sh` | Route incoming mail |

## Best Practices

1. **Always use tags** in outgoing emails
2. **One session per project/context** - don't overload
3. **Close completed sessions** - keep registry clean
4. **Use client prefixes** for client-specific sessions
5. **Review routing rules** periodically

---

*Package version: 1.0.0*
