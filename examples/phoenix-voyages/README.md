# Phoenix Voyages Workspace Example

Reference implementation for a Host Travel Agency operations workspace.

## Business Context

**Organization:** Phoenix Voyages
**Industry:** Travel / Host Agency
**Workspace Purpose:** ITA (Independent Travel Advisor) management, recruitment, marketing

## Host Agency Model

Phoenix Voyages is a **Host Agency** - clients are Travel Advisors, not travelers.

| Role | Description |
|------|-------------|
| Host Agency | Phoenix Voyages - provides infrastructure |
| ITA | Independent Travel Advisor - sells travel |
| Traveler | End customer (ITA's client, not Phoenix's) |
| Consortium | Travel Leaders Network |

## Entity Types

| Entity | Registry File | Description |
|--------|--------------|-------------|
| Advisors | `advisors.yaml` | Independent Travel Advisors |
| Suppliers | `suppliers.yaml` | Cruise lines, tour operators |

## Session Prefixes

| Prefix | Type | Example |
|--------|------|---------|
| R | Recruitment | R-001 New ITA Prospect |
| A | Advisor | A-001 Jane Smith Account |
| M | Marketing | M-001 Spring Campaign |
| S | Supplier | S-001 Carnival Partnership |
| I | Internal | I-OPS Operations Hub |

## MCP Servers (Planned)

- **telegram** - Notifications
- **phoenix-email** - cPanel IMAP (claude@travelhost.example.com)
- **groundhogg** - Marketing automation CRM
- **later-dev** - Social media scheduling
- **nextcloud** - File sharing
- **vaultwarden** - Credential management
- **docuseal** - E-signatures
- **quickbooks** - Accounting
- **phoenix-backoffice** - Custom back-office API

## Skills

### Advisor Management
- `/advisor` - Advisor operations
- `/recruit` - Recruitment workflow
- `/onboard-ita` - New ITA onboarding

### Marketing
- `/campaign` - Marketing campaigns
- `/social` - Social media management
- `/newsletter` - Email newsletter

### Operations
- `/status` - System health check
- `/email` - Email management
- `/report` - Generate reports

## Folder Structure

```
Phoenix-Voyages/
├── CLAUDE.md
├── advisors.yaml
├── suppliers.yaml
├── .mcp.json
│
├── advisors/
│   └── [advisor-code]/
│       ├── profile.md
│       ├── contacts.yaml
│       └── communications/
│
├── suppliers/
│   └── [supplier-code]/
│       ├── info.md
│       └── contracts/
│
├── marketing/
│   ├── campaigns/
│   ├── templates/
│   └── assets/
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

### ITA Recruitment Flow
1. Lead comes in (email, social, referral)
2. Create R-xxx session
3. Initial outreach from claude@
4. Track touchpoints in session
5. If interested, schedule call
6. Convert to onboarding

### ITA Onboarding Flow
1. Create advisor entry in `advisors.yaml`
2. Create advisor folder structure
3. Create A-xxx session
4. Send welcome package
5. Schedule training sessions
6. Create followups for check-ins

### Marketing Campaign Flow
1. Create M-xxx session
2. Define campaign in session
3. Create content in Later.dev
4. Set up email sequence in Groundhogg
5. Track metrics and adjust

## Key Learnings

1. **Host vs Retail** - Advisors are clients, not travelers
2. **Dual email identity** - Claude@ for automation, user@ for personal
3. **Supplier relationships** - Track commission structures per supplier
4. **Consortium compliance** - Travel Leaders Network requirements
