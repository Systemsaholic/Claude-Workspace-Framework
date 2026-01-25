# Deploy Email System

Step-by-step guide to deploying the dual-identity Email System package.

## Prerequisites

- [ ] Session Hub deployed
- [ ] Email server access (cPanel, Google Workspace, etc.)
- [ ] DNS configured for sending domain
- [ ] Email MCP server available or planned

## Step 1: Create Email Accounts

### Claude's Identity

Create dedicated email for AI assistant:

```
claude@[domain]
```

This email is used for:
- Automated communications
- Follow-up sequences
- System notifications
- AI-initiated outreach

### User Identity (On-Behalf-Of)

Identify existing user email(s):

```
user@[domain]
info@[domain]
```

These are used when Claude responds as the user.

## Step 2: Configure Email in CLAUDE.md

Add email configuration to workspace CLAUDE.md:

```markdown
### Email Modes

| Mode | Email | Use For |
|------|-------|---------|\
| **Claude's Email** | claude@[domain] | Automated comms, follow-ups |
| **On Behalf of User** | user@[domain] | Personal responses |

**Default behavior:**
- Responding to user's inbox → use user@[domain]
- New automated communications → use claude@[domain]
```

## Step 3: Set Up Email Tag System

Configure email tags in session-registry.yaml:

```yaml
email_tags:
  P:P-001:
    type: project
    session_id: P-001
    context: WebsiteRedesign
    thread_ids: []
    created_at: "2026-01-25T00:00:00Z"
```

### Tag Format

```
[TYPE:SESSION_ID CONTEXT] Subject Line
```

Examples:
- `[P:P-001 Website] Design review feedback`
- `[S:S-001 BugFix] Issue resolved`
- `[I:OPS Operations] Weekly report`

## Step 4: Create Email MCP Server

If building custom email MCP, include these tools:

### Required Tools

| Tool | Purpose |
|------|---------|
| `email_list` | List emails with filters |
| `email_read` | Read email content |
| `email_send` | Send email |
| `email_reply` | Reply to thread |
| `email_search` | Search emails |
| `email_move` | Move to folder |
| `email_label` | Apply labels/tags |

### Tool Schemas

```python
# email_send schema
{
    "from_identity": "claude|user",
    "to": ["recipient@example.com"],
    "cc": [],
    "bcc": [],
    "subject": "Subject line",
    "body": "Email body (HTML or plain)",
    "reply_to_message_id": "optional-thread-id",
    "session_tag": "P:P-001"
}
```

## Step 5: Create /email Skill

```markdown
# /email

Draft and send emails with proper identity and tagging.

## Usage

/email [action] [options]

## Actions

| Action | Description |
|--------|-------------|
| `draft` | Create draft for review |
| `send` | Send immediately |
| `reply` | Reply to thread |
| `check` | Check inbox |

## Identity Selection

- Responding to user's inbox: Uses user@[domain]
- New automated communication: Uses claude@[domain]
- Override with `--as claude` or `--as user`

## Tagging

Automatically applies session tag based on context.
Override with `--tag P:P-001`
```

## Step 6: Configure Routing Rules

Add email domain routing to session-registry.yaml:

```yaml
routing_rules:
  domains:
    client.com: C
    partner.com: P
    supplier.com: S
```

## Step 7: Set Up Email Templates

Create templates directory:

```bash
mkdir -p ~/[WORKSPACE_NAME]/operations/templates/email
```

Example templates:

### followup.md
```markdown
Subject: Following up on {{topic}}

Hi {{name}},

I wanted to follow up on {{topic}} from our conversation on {{date}}.

{{body}}

Best regards,
{{signature}}
```

### introduction.md
```markdown
Subject: Introduction - {{company}}

Hi {{name}},

{{intro_body}}

Looking forward to connecting.

Best,
{{signature}}
```

## Step 8: Test Email Flow

### Test 1: Send as Claude

```
/email send --as claude --to test@example.com --subject "Test from Claude"
```

Verify:
- Sent from claude@[domain]
- Proper signature

### Test 2: Send as User

```
/email send --as user --to test@example.com --subject "Test on behalf"
```

Verify:
- Sent from user@[domain]
- Proper signature

### Test 3: Session Tagging

```
/email send --tag P:P-001 --subject "Tagged email test"
```

Verify:
- Subject includes `[P:P-001 Context]`
- Thread tracked in session

## Step 9: Configure Inbox Processing

### Manual Processing

Create `/inbox` skill for checking emails:

```markdown
# /inbox

Process incoming emails and route to sessions.

## Workflow

1. Fetch unread emails
2. Parse subject for existing tags
3. Match sender domain to routing rules
4. Match keywords to routing rules
5. Route to appropriate session
6. Apply labels/move to folders
```

### Automated Processing

Set up n8n workflow or webhook to:
1. Trigger on new email
2. Call Claude with email content
3. Let Claude route and respond

## Troubleshooting

### Emails Not Sending

1. Check SMTP credentials
2. Verify DNS (SPF, DKIM, DMARC)
3. Check sending limits

### Wrong Identity Used

1. Review CLAUDE.md email rules
2. Check skill invocation parameters
3. Verify default behavior

### Tags Not Parsing

1. Check tag format in subject
2. Verify email_tags registry
3. Review parsing logic

## Security Considerations

- Store credentials in secure vault (Vaultwarden)
- Use app-specific passwords where available
- Enable 2FA on email accounts
- Regular credential rotation

## Next Steps

- [ ] Configure notification layer
- [ ] Set up email templates
- [ ] Create inbox processing workflow
- [ ] Test end-to-end email flow

---

*Playbook version: 1.0.0*
