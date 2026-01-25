# Framework Purity Rules

This document defines what belongs in the Claude Workspace Framework versus what stays project-specific.

## Core Principle

> The framework must work for ANY deployment without modification.
> If it contains a specific name, credential, or business logic, it doesn't belong here.

---

## What BELONGS in the Framework

### Packages (`/packages/`)
- Generic, reusable system components
- Memory system, session hub, email patterns, etc.
- Must use placeholder values, not real ones

### Playbooks (`/playbooks/`)
- Step-by-step deployment guides
- Reference placeholder values like `your-domain.com`
- Explain concepts, don't hardcode specifics

### Templates (`/templates/`)
- Skeleton files with placeholder content
- Comments explaining what to customize
- Example structure, not real data

### Scripts (`/scripts/`)
- Helper utilities that work anywhere
- Use environment variables, not hardcoded values

### Examples (`/examples/`)
- Fictional reference implementations
- Show patterns, not real client data
- Use obviously fake names (Acme Corp, Jane Doe)

---

## What NEVER Belongs in the Framework

### Credentials & Secrets
- API keys, tokens, passwords
- SSH keys, certificates
- OAuth credentials
- Database connection strings

### Project-Specific Data
- Real client/customer names
- Real email addresses
- Real company names (yours or clients')
- Real phone numbers or addresses
- Real domain names (except example.com)

### Business Logic
- Pricing, rates, fees
- Client-specific workflows
- Organization-specific policies
- Custom integrations for specific services

### Runtime Files
- Logs, caches, temp files
- Active session data
- Memory state (followups.yaml with real tasks)
- Registry data (real clients, advisors)

---

## Placeholder Conventions

Use these placeholder patterns in framework code:

| Type | Placeholder | Example |
|------|-------------|---------|
| Domain | `example.com`, `your-domain.com` | `claude@example.com` |
| Company | `Acme Corp`, `Example Inc` | `client: Acme Corp` |
| Person | `Jane Doe`, `John Smith` | `contact: Jane Doe` |
| Email | `user@example.com` | `notify: admin@example.com` |
| API Key | `your-api-key-here`, `sk_test_xxx` | `API_KEY=your-api-key-here` |
| Phone | `+1-555-0100` | (555 prefix is reserved for fiction) |
| IP | `192.0.2.x`, `203.0.113.x` | (TEST-NET ranges) |

---

## Validation Checklist

Before pushing to the framework, verify:

- [ ] No real company names (search for your clients)
- [ ] No real email addresses (search for `@` excluding `@example`)
- [ ] No API keys or tokens (search for `sk_`, `api_`, `token`)
- [ ] No real domains (search for `.com`, `.io`, etc.)
- [ ] No hardcoded IPs (except test ranges)
- [ ] No absolute paths to your systems
- [ ] No references to specific servers or hostnames

---

## Directory Structure in Deployments

```
my-workspace/                    # Project repo root
├── framework/                   # ← SUBTREE: Only this syncs with upstream
│   ├── packages/
│   ├── playbooks/
│   ├── templates/
│   └── scripts/
│
├── workspace/                   # ← PROJECT-SPECIFIC: Never pushed upstream
│   ├── CLAUDE.md               # Your customized context
│   ├── registries/             # Your real clients, data
│   ├── skills/                 # Your custom skills
│   └── memory/                 # Your followups, checks
│
├── mcp-servers/                 # ← PROJECT-SPECIFIC: Your MCP implementations
│
└── .env                         # ← PROJECT-SPECIFIC: Your secrets
```

**Only `framework/` syncs with GitHub. Everything else stays local.**

---

## When in Doubt

Ask yourself:
1. Would this work if copied to a completely different organization?
2. Does this contain any information about real people or companies?
3. Could this expose credentials if made public?

If any answer is "no" or "yes" (for #2/#3), it doesn't belong in the framework.
