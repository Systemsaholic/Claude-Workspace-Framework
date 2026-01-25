# IT-Admin Workspace Example

Reference implementation for an MSP (Managed Service Provider) operations workspace.

## Business Context

**Organization:** Acme MSP
**Industry:** IT Services / MSP
**Workspace Purpose:** Client management, ticket routing, project tracking

## Entity Types

| Entity | Registry File | Description |
|--------|--------------|-------------|
| Clients | `clients.yaml` | MSP client organizations |
| Projects | `projects.yaml` | Client projects |
| Deadlines | `deadline-registry.yaml` | Time-sensitive items |

## Session Prefixes

| Prefix | Type | Example |
|--------|------|---------|
| P | Projects | P-001 Website Migration |
| S | Support | S-001 Server Outage |
| C | Client | C-001 ACME Corp Account |
| I | Internal | I-OPS Operations Hub |

## MCP Servers Deployed

- **telegram** - Notifications
- **google-workspace** - Gmail, Calendar, Drive
- **it-admin-email** - Custom cPanel IMAP
- **n8n** - Workflow automation
- **pandadoc** - Proposals and contracts

## Skills

### Client Management
- `/client` - Client operations
- `/onboard` - New client onboarding

### Project Management
- `/project` - Project operations
- `/deadline` - Deadline tracking

### Operations
- `/status` - System health check
- `/email` - Email management
- `/report` - Generate reports

## Folder Structure

```
IT-Admin/
├── CLAUDE.md
├── clients.yaml
├── projects.yaml
├── deadline-registry.yaml
├── .mcp.json
│
├── clients/
│   └── [client-code]/
│       ├── notes.md
│       ├── contacts.yaml
│       └── projects/
│
├── operations/
│   ├── session-registry.yaml
│   ├── skills/
│   ├── scripts/
│   └── memory/
│       ├── followups.yaml
│       └── checks.yaml
│
└── knowledge-base/
    ├── sops/
    └── guides/
```

## Integration Patterns

### Client Onboarding Flow
1. Receive inquiry email
2. Route to I-OPS session
3. Create client entry in `clients.yaml`
4. Create client folder structure
5. Create initial session (C-xxx)
6. Send welcome email

### Support Ticket Flow
1. Email arrives from client
2. Parse subject for tags
3. Route to existing session or create S-xxx
4. Track in session until resolved
5. Create followup if needed

## Key Learnings

1. **Entity codes** - Short codes (ACME, GLOBEX) make routing easier
2. **Session inheritance** - Projects inherit from client sessions
3. **Deadline escalation** - Auto-notify Telegram on overdue items
