# Notification Layer Package

Alert system for urgent notifications, escalations, and human-in-the-loop decisions.

## Overview

The Notification Layer provides:
- **Telegram Alerts** - Real-time notifications to admin
- **Escalation Logic** - Route uncertain decisions to humans
- **Priority Levels** - Severity-based alerting
- **Action Buttons** - Interactive decision making

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Notification Layer                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │   Claude     │───▶│  Telegram    │                   │
│  │   Session    │    │    MCP       │                   │
│  └──────────────┘    └──────┬───────┘                   │
│                             │                            │
│                             ▼                            │
│                    ┌──────────────┐                      │
│                    │  Admin Chat  │                      │
│                    │  or Group    │                      │
│                    └──────┬───────┘                      │
│                             │                            │
│                    [User Decision]                       │
│                             │                            │
│                             ▼                            │
│                    ┌──────────────┐                      │
│                    │  n8n Webhook │ (for callbacks)      │
│                    └──────────────┘                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Components

```
notification-layer/
├── mcp-servers/
│   └── telegram-mcp/       # Telegram bot MCP
├── prompts/
│   └── escalation.md       # Escalation decision logic
└── templates/
    └── alert-templates.md  # Standard alert formats
```

## Telegram MCP Configuration

### .mcp.json

```json
{
  "telegram": {
    "command": "/path/to/telegram-mcp/.venv/bin/python",
    "args": ["-m", "telegram_mcp.server"],
    "cwd": "/path/to/telegram-mcp",
    "env": {
      "TELEGRAM_BOT_TOKEN": "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ",
      "TELEGRAM_CHAT_ID": "123456789"
    }
  }
}
```

### Required Tools

| Tool | Purpose |
|------|---------|
| `send_message` | Send plain text message |
| `send_alert` | Send formatted alert with level |
| `send_code_block` | Send code/log snippets |
| `server_status` | Check bot connection |

## Alert Levels

| Level | Icon | Use Case | Example |
|-------|------|----------|---------|
| `info` | ℹ️ | Informational | Task completed |
| `success` | ✅ | Positive outcome | Backup successful |
| `warning` | ⚠️ | Attention needed | Disk 80% full |
| `error` | ❌ | Problem occurred | Service down |
| `critical` | 🚨 | Immediate action | Security breach |

## Alert Templates

### Simple Message

```python
send_message(text="Task completed successfully")
```

**Output:**
```
Task completed successfully
```

### Formatted Alert

```python
send_alert(
    title="Daily Health Check",
    message="All systems operational",
    level="success"
)
```

**Output:**
```
✅ Daily Health Check

All systems operational
```

### Error Alert

```python
send_alert(
    title="Service Down",
    message="Web server not responding\nHost: web-01\nLast seen: 5 minutes ago",
    level="error"
)
```

**Output:**
```
❌ Service Down

Web server not responding
Host: web-01
Last seen: 5 minutes ago
```

### Code Block

```python
send_code_block(
    code="Error: Connection refused\nat connect() line 42",
    language="text",
    caption="Server error log"
)
```

## Escalation Patterns

### Pattern 1: Uncertain Routing

When Claude can't confidently route an email:

```python
# In email routing logic
if confidence < 0.85:
    send_alert(
        title="Email Routing Decision",
        message=f"""
From: {sender}
Subject: {subject}

Suggested session: {suggested_session}
Confidence: {confidence}%

Reply with session ID to route, or 'ignore' to skip.
        """,
        level="warning"
    )
```

### Pattern 2: Approval Required

When action needs human approval:

```python
send_alert(
    title="Approval Needed",
    message=f"""
Action: Send invoice to {client}
Amount: ${amount}

Reply 'approve' to proceed or 'cancel' to abort.
    """,
    level="info"
)
```

### Pattern 3: Error Escalation

When Claude encounters an error it can't resolve:

```python
send_alert(
    title="Action Failed",
    message=f"""
Task: {task_description}
Error: {error_message}

Attempted {retry_count} times.
Manual intervention may be required.
    """,
    level="error"
)
```

## Interactive Buttons (Advanced)

With n8n webhook integration, add action buttons:

### Telegram with Inline Buttons

```python
send_message_with_buttons(
    text="New support request from client",
    buttons=[
        {"text": "View Ticket", "callback_data": "view_ticket_123"},
        {"text": "Assign to Me", "callback_data": "assign_123"},
        {"text": "Ignore", "callback_data": "ignore_123"}
    ]
)
```

### n8n Webhook Handler

```
Telegram Button Click
    → n8n receives callback_data
    → n8n triggers appropriate action
    → n8n sends confirmation back to Claude session
```

## Multiple Workspaces

Use different chat IDs for different workspaces:

```json
{
  "telegram-itadmin": {
    "env": {
      "TELEGRAM_BOT_TOKEN": "same-bot-token",
      "TELEGRAM_CHAT_ID": "111111111"
    }
  },
  "telegram-phoenix": {
    "env": {
      "TELEGRAM_BOT_TOKEN": "same-bot-token",
      "TELEGRAM_CHAT_ID": "222222222"
    }
  }
}
```

Or use different channels in same chat:

```python
# Add workspace prefix to messages
send_alert(
    title="[Phoenix] New Advisor Application",
    message="...",
    level="info"
)
```

## Deployment

### Prerequisites

1. Telegram account
2. Bot created via @BotFather
3. Chat/group ID obtained

### Steps

1. **Create Telegram Bot**
   ```
   1. Message @BotFather on Telegram
   2. Send /newbot
   3. Follow prompts to name your bot
   4. Save the bot token
   ```

2. **Get Chat ID**
   ```
   1. Add bot to a group, or message it directly
   2. Send a message to the chat
   3. Visit: https://api.telegram.org/bot<TOKEN>/getUpdates
   4. Find chat.id in the response
   ```

3. **Configure MCP**
   ```json
   "telegram": {
     "env": {
       "TELEGRAM_BOT_TOKEN": "your-token",
       "TELEGRAM_CHAT_ID": "your-chat-id"
     }
   }
   ```

4. **Test Connection**
   ```
   server_status()
   send_message(text="Test from Claude workspace")
   ```

## Usage Patterns

### Startup Notification

```python
# In session startup
send_alert(
    title="Session Started",
    message=f"Claude session {session_id} is now active",
    level="info"
)
```

### Completion Notification

```python
# After completing major task
send_alert(
    title="Task Complete",
    message=f"Completed: {task_description}",
    level="success"
)
```

### Daily Summary

```python
# End of day summary
send_message(text=f"""
📊 Daily Summary - {date}

✓ Emails processed: {email_count}
✓ Tasks completed: {task_count}
✓ Issues resolved: {issue_count}

No action required.
""")
```

## Best Practices

1. **Don't over-notify** - Only alert for important items
2. **Use appropriate levels** - Match severity to situation
3. **Include context** - Provide enough info to act
4. **Group related alerts** - Don't spam with individual items
5. **Provide actionable info** - What should the human do?
6. **Mute during off-hours** - Respect notification settings

## Integration Points

| System | Integration |
|--------|-------------|
| **Session Hub** | Escalate uncertain routing |
| **Memory System** | Alert on failed scheduled tasks |
| **Email System** | Notify on important emails |
| **Skills** | Skills can send notifications |

---

*Package version: 1.0.0*
