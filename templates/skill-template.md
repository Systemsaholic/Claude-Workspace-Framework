# /[command-name]

[One-line description of what this skill does]

## Purpose

[Detailed explanation of what this skill does and when to use it]

## Usage

```
/[command-name] [required-arg] [optional-arg]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `arg1` | Yes | Description of first argument |
| `arg2` | No | Description of optional argument (default: value) |

## Examples

```
/[command-name] example-value
/[command-name] value --flag
/[command-name] "multi word value"
```

## Workflow

1. **Validate inputs** - Check required arguments
2. **Gather context** - Read relevant files/data
3. **Perform action** - Execute the main task
4. **Handle errors** - Gracefully handle failures
5. **Report results** - Show outcome to user

## Dependencies

- **Files:** `[file.yaml]` - [why needed]
- **MCP Servers:** `[mcp-name]` - [why needed]
- **Other Skills:** `/[skill]` - [why needed]

## Output

[Describe what the skill produces - formatted text, file changes, emails sent, etc.]

### Success Output

```
✓ [Command] completed successfully

[Details of what was done]
```

### Error Output

```
✗ [Command] failed

Error: [error message]
[Suggested remediation]
```

## Notes

- [Important note 1]
- [Important note 2]
- [Edge cases to be aware of]

---

*Skill version: 1.0.0*
