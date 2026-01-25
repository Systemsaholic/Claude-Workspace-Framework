# Memory System Package

Persistent state management across Claude sessions via file-based storage.

## Quick Start - Slash Commands

| Command | Purpose |
|---------|---------|
| `/check-create` | Create new recurring check (daily, weekly, interval) |
| `/check-list` | View all active checks and status |
| `/followup-create` | Create one-time scheduled task |
| `/followup-list` | View pending/completed followups |
| `/session-save` | Save current session for future resume |
| `/session-list` | List tmux sessions and resume capability |

## Overview

The Memory System provides:
- **Followups** - One-time scheduled tasks
- **Checks** - Recurring scheduled tasks (daily, weekly, monthly, interval)
- **Recent Actions** - Activity log
- **Email Memory** - Saved email archive
- **Task Locking** - Prevents duplicate session spawning
- **Session Resume** - Save/restore session context

## How It Works

1. **Session ID**: Each Claude run in tmux uses session format X-### (e.g., P-001, M-001)
2. **Read on Start**: Claude reads memory files to understand pending work
3. **Write on Action**: When Claude takes action, it logs to `recent-actions.yaml`
4. **Schedule Followups**: Use `/followup-create` or manually add to `followups.yaml`
5. **Schedule Checks**: Use `/check-create` or manually add to `checks.yaml`
6. **Session Resume**: Use `/session-save` to enable context recovery after restarts
7. **Auto-Commit**: After session, changes push to GitHub via `auto-commit.sh`

## Components

```
memory-system/
├── memory/
│   ├── followups.yaml      # One-time tasks
│   ├── checks.yaml         # Recurring tasks
│   ├── recent-actions.yaml # Activity log
│   └── emails/             # Saved email archive
├── scripts/
│   ├── memory-cron.sh      # Processes due items
│   ├── check-due-items.sh  # Parses YAML for due items
│   └── route-to-session.sh # Routes to tmux sessions
└── prompts/
    └── process-followup.md # Prompt for handling items
```

## Cron-Based Execution

A cron job runs every minute to check for due items:

```bash
* * * * * /path/to/workspace/operations/scripts/memory-cron.sh
```

**Flow:**
1. `check-due-items.sh` parses `followups.yaml` and `checks.yaml`
2. Items with `due` timestamp in the past are returned
3. `memory-cron.sh` processes each item:
   - **Checks lock file** before processing (prevents duplicates)
   - If `target_session` is set: Routes prompt to existing tmux session
   - Otherwise: Spawns a new Claude session to handle it
4. `auto-commit.sh` pushes any changes to GitHub

## Task Locking Mechanism

To prevent duplicate sessions from being spawned for the same task (e.g., if cron runs while a previous task is still processing), the memory system uses file-based locking.

**Lock File Location:** `/tmp/memory-task-{item_id}.lock`

**Lock Behavior:**
- Before processing any item, the cron script checks for an existing lock file
- If a lock file exists and is **less than 5 minutes old**: Skip the item
- If a lock file exists and is **more than 5 minutes old**: Consider it stale, remove it, and proceed
- Lock file is created before processing and removed after completion

**Lock Check Flow:**
```
Item "maint-reboot-123" becomes due
    │
    ▼
Check: Does /tmp/memory-task-maint-reboot-123.lock exist?
    │
    ├── Yes, age < 5 min → SKIP (already being processed)
    │
    ├── Yes, age >= 5 min → Remove stale lock, proceed
    │
    └── No → Create lock, process item, remove lock
```

**Troubleshooting Duplicate Sessions:**

If you see duplicate Claude sessions for the same task:
1. Check for orphaned lock files: `ls -la /tmp/memory-task-*.lock`
2. Check lock file age: `stat /tmp/memory-task-{id}.lock`
3. Manually remove stale locks: `rm /tmp/memory-task-{id}.lock`
4. Check cron logs: `tail -100 /tmp/memory-watcher.log | grep LOCK`

**Log Messages for Locking:**
- `LOCK ACQUIRED: {item_id}` - Lock created, processing started
- `LOCK RELEASED: {item_id}` - Processing complete, lock removed
- `SKIPPED: {item_id} - lock file exists ({N}s old)` - Item skipped due to active lock
- `STALE LOCK: {item_id} - lock file expired ({N}s), removing` - Old lock cleaned up

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
      client_name: Jane Doe
      client_email: jane@example.com
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
| `scheduled_maintenance` | Maintenance window task |
| `custom` | Freeform task |

### Maintenance Windows

For tasks that should only run during off-hours:

```yaml
context:
  maintenance_window: "00:00-04:00 EST"  # Only runs in this window
```

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
    skill: /pipeline-review
    description: Weekly pipeline review
    status: active
```

### Recurrence Types

| Type | Fields | Example |
|------|--------|---------|
| `daily` | `recurrence_hour` | Every day at 6am |
| `weekly` | `recurrence_day`, `recurrence_hour` | Monday at 9am |
| `monthly` | `recurrence_date`, `recurrence_hour` | 1st of month at 8am |
| `interval` | `interval_hours` | Every 4 hours |

## Session Resume Capability

Claude sessions can be resumed after tmux restarts, preserving conversation context.

### How It Works

```
1. Run /session-save (or: session-manager.sh save-session M-001)
   └── Saves .jsonl path to ~/sessions/M-001/claude_session.txt

2. Later, tmux session dies or is recreated
   └── session-manager.sh create M-001

3. Script finds saved reference
   └── Runs "claude --resume" instead of fresh start

4. Context restored!
```

### Commands

```bash
# Save current session for future resume
/session-save
# or: session-manager.sh save-session M-001

# Check what sessions can be resumed
/session-list
# or: session-manager.sh info M-001

# Create session (auto-resumes if saved)
session-manager.sh create M-001

# Create without resume
session-manager.sh create-fresh M-001
```

### Best Practices

- Run `/session-save` before ending important sessions
- Run `/session-save` before scheduled maintenance
- Use session categories: P (Projects), S (Support), M (Monitoring), etc.
- Long-running monitors should use the M category (e.g., M-001)

## Scheduling Tasks to Existing Sessions

Use `target_session` to route scheduled prompts to a running tmux session:

```yaml
- id: maint-reboot-001
  created_by_session: main
  created_at: 2026-01-23T16:00:00
  due: 2026-01-24T00:30:00-05:00
  type: scheduled_maintenance
  description: "Reboot servers and monitor recovery"
  target_session: main  # Routes to existing tmux session
  context:
    servers:
      - name: Primary Server
        ip: 192.0.2.10
  status: pending
```

When the `due` time arrives:
1. Cron detects the item
2. Checks if tmux session `main` exists
3. Sends the prompt directly to that session
4. Claude in that session receives and processes the task

This is useful for:
- Deferred maintenance during off-hours
- Scheduled reboots with monitoring
- Any task that should continue in an existing context

## Recent Actions

Activity log for tracking what Claude has done.

```yaml
# recent-actions.yaml

actions:
  - timestamp: "2026-01-25T14:30:00Z"
    session: P-001
    action: sent_email
    details: "Sent project update to client"
    cost: 0.02  # API cost estimate

max_entries: 100  # Rotate when exceeded
```

## Session Linking

Every entry includes:
- `created_by_session`: Session ID that created it
- `completed_by_session`: Session ID that resolved it (if applicable)

This allows tracing any action back to its origin for debugging or review.

## Email Memory (Archive)

Claude's email memory is stored in `emails/`:
- `archive/` - Saved email JSON files
- `threads/` - Thread tracking
- `index.json` - Searchable index

Use MCP tools:
```python
save_to_memory(uid="123", tags=["important"])
list_saved_emails(client="acme")
search_memory(query="invoice")
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
   cp framework/packages/memory-system/scripts/memory-cron.sh operations/scripts/
   chmod +x operations/scripts/memory-cron.sh
   ```

4. **Add cron job**
   ```bash
   crontab -e
   # Add: * * * * * /path/to/operations/scripts/memory-cron.sh
   ```

## Best Practices

1. **Use descriptive IDs** - `followup-client-approval` not `f001`
2. **Include all context** - Future Claude needs full info
3. **Set realistic due times** - Account for timezone
4. **Review checks weekly** - Disable unused ones
5. **Rotate action log** - Keep max 100-200 entries
6. **Run /session-save** - Before maintenance or ending important sessions

## Integration Points

| System | Integration |
|--------|-------------|
| **Session Hub** | Route items to sessions |
| **Email System** | Send scheduled emails |
| **Telegram** | Alert on failures |
| **Skills** | Invoke skills from checks |

---

*Package version: 1.1.0*
