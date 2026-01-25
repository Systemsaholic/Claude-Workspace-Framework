# Deploy Memory System

Step-by-step guide to deploying the Memory System package for scheduled tasks and recurring checks.

## Prerequisites

- [ ] Session Hub deployed
- [ ] Operations directory exists
- [ ] YAML parsing available (Python 3)

## Step 1: Create Memory Directory

```bash
mkdir -p ~/[WORKSPACE_NAME]/operations/memory
```

## Step 2: Deploy Followups File

```bash
cp templates/followups.yaml ~/[WORKSPACE_NAME]/operations/memory/followups.yaml
```

### Followup Structure

Each followup is a one-time scheduled task:

```yaml
followups:
  - id: followup-client-proposal
    created_by_session: P-001
    created_at: "2026-01-25T10:00:00Z"
    due: "2026-01-28T09:00:00-05:00"
    type: send_email
    description: |
      Follow up with client about proposal.
      Check if they reviewed the document.
    context:
      client_name: John Smith
      client_email: john@example.com
      project: Website Redesign
    target_session: P-001
    status: pending
```

### Followup Types

| Type | Use Case |
|------|----------|
| `send_email` | Automated email followup |
| `check_status` | Verify something happened |
| `review` | Human review needed |
| `reminder` | Simple notification |
| `custom` | Workflow-specific |

## Step 3: Deploy Checks File

```bash
cp templates/checks.yaml ~/[WORKSPACE_NAME]/operations/memory/checks.yaml
```

### Check Structure

Each check is a recurring scheduled task:

```yaml
checks:
  - id: health-daily
    check_at: "2026-01-26T06:00:00Z"
    recurrence: daily
    recurrence_hour: 6
    type: health_check
    skill: /status
    description: Daily infrastructure and connectivity check
    status: active
```

### Recurrence Types

| Recurrence | Required Fields |
|------------|-----------------|
| `daily` | `recurrence_hour` |
| `weekly` | `recurrence_hour`, `recurrence_day` |
| `monthly` | `recurrence_hour`, `recurrence_date` |
| `interval` | `interval_hours` |

### Check Types

| Type | Use Case |
|------|----------|
| `health_check` | System/service monitoring |
| `review` | Periodic data review |
| `report` | Generate scheduled reports |
| `custom` | Workflow-specific |

## Step 4: Create Memory Cron Skill

Create `/memory-cron` skill to process due items:

```markdown
# /memory-cron

Process due followups and checks from the memory system.

## Workflow

1. Read followups.yaml
2. Find items where `due <= now` and `status == pending`
3. Execute each followup based on type
4. Mark completed items with `status: completed`
5. Read checks.yaml
6. Find items where `check_at <= now` and `status == active`
7. Execute each check (invoke skill if specified)
8. Calculate next occurrence and update `check_at`

## Execution Schedule

Run this skill:
- Every hour via external cron/n8n
- On workspace startup
- Manually with `/memory-cron`
```

## Step 5: Create Helper Skills

### /followup Skill

```markdown
# /followup

Create a new scheduled followup.

## Usage

/followup [due-date] [description]

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| due-date | Yes | When to trigger (ISO or natural language) |
| description | Yes | What to do when triggered |

## Workflow

1. Parse due date
2. Generate unique ID
3. Add to followups.yaml
4. Confirm creation
```

### /check Skill

```markdown
# /check

Create a new recurring check.

## Usage

/check [recurrence] [description]

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| recurrence | Yes | daily/weekly/monthly/interval |
| description | Yes | What to check |
```

## Step 6: Set Up External Trigger

The memory system needs external triggering. Options:

### Option A: n8n Workflow

Create n8n workflow that:
1. Triggers every hour
2. Calls Claude with `/memory-cron`
3. Logs execution

### Option B: System Cron

```bash
# Add to crontab
0 * * * * /path/to/trigger-memory-cron.sh
```

### Option C: Manual

Run `/memory-cron` during each session start.

## Step 7: Verify Installation

```bash
# Check files exist
ls -la ~/[WORKSPACE_NAME]/operations/memory/

# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('operations/memory/followups.yaml'))"
python3 -c "import yaml; yaml.safe_load(open('operations/memory/checks.yaml'))"
```

## Step 8: Test with Sample Entry

Add a test followup:

```yaml
followups:
  - id: test-followup
    created_by_session: I-OPS
    created_at: "2026-01-25T12:00:00Z"
    due: "2026-01-25T12:05:00Z"  # 5 minutes from now
    type: reminder
    description: Test followup - verify memory system working
    status: pending
```

Run `/memory-cron` and verify it processes.

## Timezone Handling

- Store all times in ISO 8601 with timezone
- Support timezone offsets: `2026-01-25T09:00:00-05:00`
- Convert to UTC for comparison
- Display in user's local timezone

## Troubleshooting

### Followup Not Triggering

1. Check `due` timestamp format
2. Verify `status: pending`
3. Ensure timezone is correct

### Check Not Recurring

1. Verify recurrence fields match type
2. Check `status: active`
3. Confirm `check_at` is being updated

### Skill Not Invoking

1. Verify skill exists in skills folder
2. Check skill name matches exactly
3. Review skill for syntax errors

## Next Steps

- [ ] Deploy Email System
- [ ] Create workspace-specific checks
- [ ] Set up n8n trigger workflow
- [ ] Configure notification escalation

---

*Playbook version: 1.0.0*
