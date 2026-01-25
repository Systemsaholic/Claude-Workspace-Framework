# Memory System Package

Persistent state management across Claude sessions via file-based storage.

## Overview

The Memory System provides:
- **Followups** - One-time scheduled tasks
- **Checks** - Recurring scheduled tasks
- **Recent Actions** - Activity log
- **Email Memory** - Saved email archive

## Components

```
memory-system/
├── memory/
│   ├── followups.yaml      # One-time tasks
│   ├── checks.yaml         # Recurring tasks
│   ├── recent-actions.yaml # Activity log
│   └── emails/             # Saved email archive
├── scripts/
│   └── memory-cron.sh      # Processes due items
└── prompts/
    └── process-followup.md # Prompt for handling items
```

## Followups

One-time tasks that trigger at a specific time.

### Structure

```yaml
# followups.yaml

followups:
  - id: followup-001
    created_by_session: P-001
    created_at: "2026-01-25T10:00:00Z"
    due: "2026-01-28T09:00:00-05:00"
    type: send_email
    description: |
      Follow up with client about project approval.
      They requested time to review the proposal.
    context:
      client_name: John Smith
      client_email: john@acme.com
      project: Website Redesign
    target_session: P-001  # Route to existing session
    status: pending        # pending, completed, cancelled
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier |
| `created_by_session` | Yes | Session that created this |
| `created_at` | Yes | Creation timestamp |
| `due` | Yes | When to trigger (ISO 8601 with timezone) |
| `type` | Yes | Task type (send_email, check_status, review, custom) |
| `description` | Yes | What Claude should do |
| `context` | No | Additional data needed |
| `target_session` | No | Route to specific session |
| `status` | Yes | pending, completed, cancelled |

### Task Types

| Type | Description |
|------|-------------|
| `send_email` | Draft and send an email |
| `check_status` | Verify status of something |
| `review` | Review a document/ticket/item |
| `reminder` | Simple reminder notification |
| `custom` | Freeform task |

## Checks

Recurring tasks that repeat on a schedule.

### Structure

```yaml
# checks.yaml

checks:
  - id: health-daily
    check_at: "2026-01-26T06:00:00Z"
    recurrence: daily
    recurrence_hour: 6
    type: health_check
    skill: /health
    description: Daily infrastructure health check
    status: active  # active, paused, disabled

  - id: pipeline-weekly
    check_at: "2026-01-27T09:00:00Z"
    recurrence: weekly
    recurrence_day: monday
    recurrence_hour: 9
    type: review
    skill: /recruitment-pipeline
    description: Weekly recruitment pipeline review
    status: active
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique identifier |
| `check_at` | Yes | Next scheduled run |
| `recurrence` | Yes | daily, weekly, monthly, interval |
| `recurrence_hour` | Yes | Hour to run (0-23) |
| `recurrence_day` | For weekly | Day of week |
| `recurrence_date` | For monthly | Day of month |
| `interval_hours` | For interval | Hours between runs |
| `type` | Yes | Check type |
| `skill` | No | Skill to invoke |
| `description` | Yes | What to check |
| `status` | Yes | active, paused, disabled |

### Recurrence Types

| Type | Fields | Example |
|------|--------|---------|
| `daily` | `recurrence_hour` | Every day at 6am |
| `weekly` | `recurrence_day`, `recurrence_hour` | Monday at 9am |
| `monthly` | `recurrence_date`, `recurrence_hour` | 1st of month at 8am |
| `interval` | `interval_hours` | Every 4 hours |

## Recent Actions

Activity log for tracking what Claude has done.

### Structure

```yaml
# recent-actions.yaml

actions:
  - timestamp: "2026-01-25T14:30:00Z"
    session: P-001
    action: sent_email
    details: "Sent project update to client"
    cost: 0.02  # API cost estimate

  - timestamp: "2026-01-25T14:15:00Z"
    session: I-OPS
    action: health_check
    details: "Completed daily health check - all systems OK"
    cost: 0.01

max_entries: 100  # Rotate when exceeded
```

## Memory Cron

Background script that processes due items.

### How It Works

1. Runs every minute via system cron
2. Scans `followups.yaml` for due items
3. Scans `checks.yaml` for due items
4. Routes items to target session OR spawns new Claude
5. Marks followups as completed
6. Reschedules checks for next occurrence

### Setup

```bash
# Add to crontab
* * * * * /path/to/workspace/operations/scripts/memory-cron.sh
```

### Script Flow

```bash
#!/bin/bash
# memory-cron.sh

WORKSPACE=/path/to/workspace
FOLLOWUPS=$WORKSPACE/operations/memory/followups.yaml
CHECKS=$WORKSPACE/operations/memory/checks.yaml

# Check for due followups
# ... parse YAML, find items where due <= now and status == pending

# Check for due checks
# ... parse YAML, find items where check_at <= now and status == active

# For each due item:
#   - If target_session exists in tmux: send to that session
#   - Else: spawn new Claude session with context

# After processing:
#   - Mark followups as completed
#   - Reschedule checks to next occurrence
```

## Deployment

### Prerequisites
- yq (YAML processor) or Python for parsing
- tmux (for session routing)
- cron (for scheduling)

### Steps

1. **Create memory folder**
   ```bash
   mkdir -p operations/memory
   ```

2. **Create empty files**
   ```bash
   echo "followups: []" > operations/memory/followups.yaml
   echo "checks: []" > operations/memory/checks.yaml
   echo "actions: []" > operations/memory/recent-actions.yaml
   ```

3. **Deploy cron script**
   ```bash
   cp scripts/memory-cron.sh operations/scripts/
   chmod +x operations/scripts/memory-cron.sh
   ```

4. **Add cron job**
   ```bash
   crontab -e
   # Add: * * * * * /path/to/operations/scripts/memory-cron.sh
   ```

## Usage

### Schedule a Followup

```yaml
# Add to followups.yaml
- id: followup-client-review
  created_by_session: P-001
  created_at: "2026-01-25T10:00:00Z"
  due: "2026-01-30T09:00:00-05:00"
  type: send_email
  description: |
    Check if client has reviewed the proposal.
    If no response, send gentle reminder.
  context:
    client_email: john@acme.com
  target_session: P-001
  status: pending
```

### Create a Recurring Check

```yaml
# Add to checks.yaml
- id: backup-verify-daily
  check_at: "2026-01-26T07:00:00Z"
  recurrence: daily
  recurrence_hour: 7
  type: health_check
  description: Verify overnight backups completed
  status: active
```

### Log an Action

```yaml
# Append to recent-actions.yaml
- timestamp: "2026-01-25T15:00:00Z"
  session: I-OPS
  action: completed_check
  details: "Verified backups - all OK"
```

## Integration Points

| System | Integration |
|--------|-------------|
| **Session Hub** | Route items to sessions |
| **Email System** | Send scheduled emails |
| **Telegram** | Alert on failures |
| **Skills** | Invoke skills from checks |

## Best Practices

1. **Use descriptive IDs** - `followup-client-approval` not `f001`
2. **Include all context** - Future Claude needs full info
3. **Set realistic due times** - Account for timezone
4. **Review checks weekly** - Disable unused ones
5. **Rotate action log** - Keep max 100-200 entries

---

*Package version: 1.0.0*
