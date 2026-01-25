# Skills Framework Package

Slash command system for triggering specific workflows and capabilities.

## Overview

Skills are markdown-defined commands that Claude can execute:
- **Discoverable** - Listed in CLAUDE.md
- **Documented** - Self-describing prompts
- **Reusable** - Same skill across sessions
- **Composable** - Skills can invoke other skills

## Structure

```
operations/
└── skills/
    ├── client.md           # /client command
    ├── email.md            # /email command
    ├── status.md           # /status command
    ├── report.md           # /report command
    └── [custom].md         # Business-specific
```

## Skill File Format

### Basic Template

```markdown
# /[command-name]

[Brief one-line description]

## Purpose

[Detailed explanation of what this skill does]

## Usage

```
/[command-name] [arguments]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `arg1` | Yes | Description |
| `arg2` | No | Description (default: value) |

## Examples

```
/[command-name] example1
/[command-name] example2 --flag
```

## Workflow

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Dependencies

- [MCP Server or file required]
- [Other dependencies]

## Output

[What the skill produces/returns]
```

## Skill Categories

### Data Lookup Skills

```markdown
# /client

Lookup client information from the registry.

## Usage

```
/client [code]
/client [partial-name]
/client list [filter]
```

## Workflow

1. Read `clients.yaml`
2. Find matching client by code or name
3. Display formatted client details
4. If folder exists, show recent activity

## Examples

```
/client ACME
/client acme corp
/client list active
```
```

### Action Skills

```markdown
# /email

Draft and send professional emails.

## Usage

```
/email [recipient] [subject]
/email draft [context]
/email reply [thread-id]
```

## Workflow

1. Gather context (recipient, subject, purpose)
2. Draft email using appropriate template
3. Show draft for approval
4. Send via appropriate email mode (Claude or proxy)
5. Log action and update session if applicable

## Dependencies

- email-mcp or gworkspace-mcp

## Examples

```
/email john@acme.com "Project Update"
/email draft follow-up on proposal
```
```

### Operational Skills

```markdown
# /status

Check status of all connected systems.

## Usage

```
/status
/status [system]
/status --detailed
```

## Workflow

1. Check each MCP server connection
2. Query system-specific health endpoints
3. Compile status summary
4. Alert if any issues detected

## Systems Checked

- MCP servers (connection test)
- Email (inbox check)
- External services (API health)

## Output

```
System Status - 2026-01-25 10:00

✓ Email (claude@domain.com) - Connected
✓ Telegram - Connected
✓ [Service] - Healthy
✗ [Service] - Error: [message]
```
```

### Workflow Skills

```markdown
# /onboard-client

Onboard a new client with full setup.

## Usage

```
/onboard-client [company-name]
```

## Workflow

1. Gather client information (interactive)
2. Create entry in `clients.yaml`
3. Create client folder structure
4. Set up billing in accounting system
5. Send welcome email
6. Create onboarding checklist
7. Log completion

## Dependencies

- yaml-registries (clients.yaml)
- email-system
- accounting-mcp (optional)

## Interactive Prompts

- Company name
- Primary contact
- Email
- Services selected
- Billing preferences
```

## Common Skills Library

### Essential Skills (Every Workspace)

| Skill | Purpose |
|-------|---------|
| `/status` | Check system connectivity |
| `/email` | Draft and send emails |
| `/help` | List available skills |

### Data Management

| Skill | Purpose |
|-------|---------|
| `/client [code]` | Lookup client |
| `/advisor [code]` | Lookup advisor |
| `/supplier [code]` | Lookup supplier |
| `/search [query]` | Search across registries |

### Operations

| Skill | Purpose |
|-------|---------|
| `/report [type]` | Generate reports |
| `/backup` | Check backup status |
| `/health` | Full health check |
| `/maintenance` | Run maintenance tasks |

### Communication

| Skill | Purpose |
|-------|---------|
| `/email` | Draft/send emails |
| `/notify [message]` | Send Telegram alert |
| `/followup [entity]` | Schedule follow-up |

### Project/Task Management

| Skill | Purpose |
|-------|---------|
| `/project-new` | Start new project |
| `/project-status` | Check project status |
| `/task-create` | Create task |
| `/task-list` | List pending tasks |

## Creating Custom Skills

### Step 1: Identify the Need

```
What repetitive task could be automated?
What workflow has multiple steps?
What lookup is done frequently?
```

### Step 2: Design the Interface

```
/skill-name [required-arg] [optional-arg]

What arguments are needed?
What's the expected output?
```

### Step 3: Document the Workflow

```markdown
## Workflow

1. Validate inputs
2. Gather additional context
3. Perform action
4. Handle errors
5. Report results
```

### Step 4: Create Skill File

```bash
# Create in skills folder
touch operations/skills/my-skill.md

# Use template
cp templates/skill-template.md operations/skills/my-skill.md
```

### Step 5: Register in CLAUDE.md

```markdown
## Available Skills

| Command | Purpose |
|---------|---------|
| `/my-skill` | Does the thing |
```

## Skill Composition

Skills can invoke other skills:

```markdown
# /weekly-report

Generate weekly status report.

## Workflow

1. Run `/status` to get system health
2. Run `/client list active` to get client count
3. Query recent actions from memory
4. Compile into formatted report
5. Run `/email` to send report
```

## Best Practices

1. **One skill, one purpose** - Keep focused
2. **Document thoroughly** - Future Claude needs context
3. **Show examples** - Demonstrate usage patterns
4. **Handle errors gracefully** - What if MCP fails?
5. **Log actions** - Track what skills do
6. **Version skills** - Note when behavior changes

## Deployment

1. Create `operations/skills/` folder
2. Add skill markdown files
3. Document in CLAUDE.md
4. Test each skill
5. Iterate based on usage

## Integration Points

| System | Integration |
|--------|-------------|
| **CLAUDE.md** | Skills listed for discovery |
| **Session Hub** | Skills can be triggered by routing |
| **Memory System** | Skills can schedule follow-ups |
| **MCP Servers** | Skills invoke MCP tools |

---

*Package version: 1.0.0*
