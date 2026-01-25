# Deploy Session Hub

Step-by-step guide to deploying the Session Hub package for a new workspace.

## Prerequisites

- [ ] VPS with SSH access configured
- [ ] Workspace directory created (`~/[WORKSPACE_NAME]/`)
- [ ] CLAUDE.md initialized
- [ ] Tailscale/network access confirmed

## Step 1: Create Operations Directory

```bash
mkdir -p ~/[WORKSPACE_NAME]/operations/memory
mkdir -p ~/[WORKSPACE_NAME]/operations/skills
mkdir -p ~/[WORKSPACE_NAME]/operations/scripts
```

## Step 2: Deploy Session Registry

Copy and customize the session registry template:

```bash
# From framework templates
cp templates/session-registry.yaml ~/[WORKSPACE_NAME]/operations/session-registry.yaml
```

### Customize for Your Workspace

Edit the session registry to define your session prefixes:

```yaml
# Example customization
counters:
  P: 0   # Projects
  S: 0   # Support
  I: 1   # Internal (I-OPS exists by default)
  C: 0   # Clients
  # Add workspace-specific prefixes
```

### Define Entity Prefixes

Map entity codes to session prefixes for automatic routing:

```yaml
entity_prefixes:
  acme: A      # ACME Corp gets A-xxx sessions
  globex: G    # Globex gets G-xxx sessions
```

## Step 3: Configure Routing Rules

Define keyword patterns for email/task routing:

```yaml
routing_rules:
  keywords:
    - pattern: "(urgent|emergency|critical)"
      priority: high
      action: alert_telegram
      description: High-priority escalation

    - pattern: "(invoice|billing|payment)"
      category: finance
      description: Financial matters

  domains:
    client.com: C
    partner.com: P
```

## Step 4: Initialize I-OPS Session

The Operations Hub (I-OPS) is the default session:

```yaml
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
      Main operations session for this workspace.
      Handles general queries, email, and routing.
    keywords:
      - operations
      - general
      - email
```

## Step 5: Create Session Management Skill

Create `/session` skill for managing sessions:

```bash
cp templates/skill-template.md ~/[WORKSPACE_NAME]/operations/skills/session.md
```

Edit to include session operations:
- Create new session
- List active sessions
- Switch session context
- Archive/close session

## Step 6: Verify Installation

Run verification checks:

```bash
# Check file structure
ls -la ~/[WORKSPACE_NAME]/operations/

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('operations/session-registry.yaml'))"

# Check permissions
stat ~/[WORKSPACE_NAME]/operations/session-registry.yaml
```

## Step 7: Test Session Creation

Test creating a new session manually:

```yaml
# Add to sessions section
P-001:
  name: Test Project
  category: project
  status: active
  created: "2026-01-25T12:00:00Z"
  last_activity: "2026-01-25T12:00:00Z"
  description: Test session for verification
  keywords:
    - test
```

Verify counter incremented:
```yaml
counters:
  P: 1  # Should now be 1
```

## Troubleshooting

### Session Not Routing

1. Check `routing_rules.keywords` patterns
2. Verify `entity_prefixes` mapping
3. Confirm session status is `active`

### Counter Not Incrementing

1. Ensure counter key matches session prefix
2. Check YAML syntax around counters section

### Email Tags Not Working

1. Verify `email_tags` section format
2. Check session_id references valid session

## Next Steps

- [ ] Deploy Memory System (`deploy-memory-system.md`)
- [ ] Deploy Email System (`deploy-email-system.md`)
- [ ] Create workspace-specific skills
- [ ] Configure notification layer

---

*Playbook version: 1.0.0*
