# Email System Package

Dual-identity email management for Claude - automated communications and on-behalf-of responses.

## Overview

The Email System provides:
- **Claude's Email** - Dedicated address for automated communications
- **Proxy Mode** - Send as the user for personal responses
- **Email Tags** - Subject line tagging for routing/tracking
- **Email Memory** - Archive important emails for reference

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Email System                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐              │
│  │ Claude Email │         │  User Email   │              │
│  │  MCP Server  │         │  MCP Server   │              │
│  └──────┬───────┘         └──────┬───────┘              │
│         │                        │                       │
│         ▼                        ▼                       │
│  claude@domain.com        user@domain.com                │
│  (Automated comms)        (Personal responses)           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Components

```
email-system/
├── mcp-servers/
│   └── email-mcp/          # Claude's email MCP
├── templates/
│   ├── email-signature.md  # Standard signature
│   └── email-templates/    # Common email templates
└── prompts/
    └── email-routing.md    # Routing decision logic
```

## Email Modes

### Mode 1: Claude's Email

| Aspect | Details |
|--------|---------|
| **Address** | `claude@domain.com` |
| **MCP Server** | `claude-email` or `workspace-email` |
| **Use Cases** | Automated follow-ups, system notifications, new threads |
| **Identity** | "Claude (Company AI Assistant)" |

### Mode 2: On-Behalf-Of (Proxy)

| Aspect | Details |
|--------|---------|
| **Address** | `user@domain.com` |
| **MCP Server** | `gworkspace` or dedicated user email MCP |
| **Use Cases** | Responding to user's inbox, client communications |
| **Identity** | Appears as the user |

## Email Tag System

### Format

```
[TYPE:SESSION_ID CONTEXT] Subject Line
```

### Components

| Part | Description | Example |
|------|-------------|---------|
| `TYPE` | Session category prefix | P, S, I, R, M |
| `SESSION_ID` | Session identifier | P-001, I-OPS |
| `CONTEXT` | Short context hint | Website, Support |
| `Subject` | Actual subject | Meeting scheduled |

### Examples

```
[P:P-001 Website] Design mockups ready for review
[S:S-042 VPN] Issue resolved - please test
[I:OPS Daily] Health check report - all systems OK
[R:R-015 Prospect] Follow-up on application
```

## MCP Server Configuration

### Claude Email MCP

```json
{
  "claude-email": {
    "command": "/path/to/email-mcp/.venv/bin/python",
    "args": ["-m", "email_mcp.server"],
    "cwd": "/path/to/email-mcp",
    "env": {
      "EMAIL_ADDRESS": "claude@domain.com",
      "EMAIL_PASSWORD": "app-password-here",
      "IMAP_HOST": "mail.domain.com",
      "IMAP_PORT": "993",
      "SMTP_HOST": "mail.domain.com",
      "SMTP_PORT": "465",
      "DISPLAY_NAME": "Claude (Company AI)"
    }
  }
}
```

### Required MCP Tools

| Tool | Purpose |
|------|---------|
| `check_inbox` | List recent emails |
| `read_email` | Get email content |
| `send_email` | Send new email |
| `reply_to` | Reply to existing thread |
| `search_emails` | Search by query |
| `save_to_memory` | Archive important email |

## Email Templates

### Standard Signature

```markdown
Best regards,
Claude
AI Assistant - [Company Name]

---
This email was sent by Claude, an AI assistant.
For urgent matters, please contact [user@domain.com].
```

### Follow-up Template

```markdown
Subject: [TYPE:SESSION_ID CONTEXT] Following up on [topic]

Hi [Name],

I wanted to follow up on [topic] from [date/context].

[Specific question or update]

Please let me know if you have any questions.

[Signature]
```

## Deployment

### Prerequisites

- Email account created (cPanel, Google Workspace, etc.)
- IMAP/SMTP access enabled
- App password generated (if 2FA enabled)

### Steps

1. **Create Claude's email account**
   ```
   Account: claude@yourdomain.com
   Note: IMAP host, SMTP host, ports
   ```

2. **Build or configure email MCP**
   ```bash
   # Clone template
   cp -r mcp-templates/email-mcp operations/mcp-servers/

   # Configure
   cd operations/mcp-servers/email-mcp
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Add to .mcp.json**
   ```json
   "workspace-email": {
     "command": "...",
     "env": {
       "EMAIL_ADDRESS": "claude@domain.com",
       ...
     }
   }
   ```

4. **Test connection**
   ```
   # In Claude session
   check_inbox(limit=5)
   ```

5. **Configure signature in CLAUDE.md**
   ```markdown
   ## Email Signature

   Use this signature for all emails:
   [signature template]
   ```

## Usage Patterns

### Sending Automated Email

```python
send_email(
    to="client@example.com",
    subject="[P:P-001 Website] Weekly status update",
    body="Hi...\n\n[content]\n\n[signature]",
    session_id="P-001"  # For tracking
)
```

### Responding to User's Inbox

```python
# Using gworkspace or user email MCP
gmail_create_draft(
    to="client@example.com",
    subject="Re: Project question",
    body="Hi...\n\n[response as user]"
)
```

### Checking for Replies

```python
# Check Claude's inbox for replies
check_inbox(limit=20, unread_only=True)

# Search for specific thread
search_emails(query='SUBJECT "[P:P-001"')
```

## Email Memory

Save important emails for future reference:

```python
# Save email to memory
save_to_memory(
    uid="12345",
    tags=["client-request", "urgent"],
    notes="Client requested timeline change"
)

# Retrieve later
list_saved_emails(session_id="P-001")
search_memory(query="timeline")
```

## Routing Logic

### Incoming Email Routing

1. **Check for tag** - `[TYPE:SESSION_ID]` in subject
2. **Check sender** - Known participant in session registry
3. **Check domain** - Domain routing rules
4. **Check keywords** - Keyword patterns
5. **Escalate** - If uncertain, alert via Telegram

### Outgoing Email Mode Selection

| Scenario | Mode | Email |
|----------|------|-------|
| New automated communication | Claude | claude@domain.com |
| Responding to user's inbox | Proxy | user@domain.com |
| Follow-up on Claude's thread | Claude | claude@domain.com |
| Client-facing from user | Proxy | user@domain.com |

## Best Practices

1. **Always use tags** in subjects for trackability
2. **Include session_id** when sending for routing
3. **Use templates** for consistency
4. **Archive important emails** to memory
5. **Check inbox regularly** for replies
6. **Clear signature** identifying AI assistant

## Integration Points

| System | Integration |
|--------|-------------|
| **Session Hub** | Route emails to sessions |
| **Memory System** | Archive emails, schedule follow-ups |
| **Notification Layer** | Alert on important emails |
| **Skills** | `/email` skill for drafting |

---

*Package version: 1.0.0*
