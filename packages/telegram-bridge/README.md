# Telegram Bridge Package

A full-featured 2-way conversation bridge between Telegram and Claude AI with MCP tool access.

## Overview

This package provides a FastAPI service that:
- Receives messages from Telegram via webhook
- Processes them through Claude API with MCP tools
- Sends responses back to Telegram

Unlike simple notification bots, this enables **true 2-way conversations** where Claude has access to all your workspace MCP tools (email, CRM, file storage, etc.).

## Architecture

```
┌──────────────┐     ┌─────────────────────────────────────────────┐
│   Telegram   │────▶│         Telegram Bridge (FastAPI)           │
│     User     │◀────│                                             │
└──────────────┘     │  ┌─────────────────────────────────────┐   │
                     │  │           Claude API                 │   │
                     │  │    (with MCP tool definitions)       │   │
                     │  └─────────────────────────────────────┘   │
                     │                    │                        │
                     │         ┌──────────┼──────────┐            │
                     │         ▼          ▼          ▼            │
                     │  ┌──────────┐ ┌─────────┐ ┌──────────┐    │
                     │  │ MCP      │ │  MCP    │ │  MCP     │    │
                     │  │ Server 1 │ │ Server 2│ │ Server N │    │
                     │  └──────────┘ └─────────┘ └──────────┘    │
                     └─────────────────────────────────────────────┘
```

## Features

- **Full MCP Tool Access**: Use all workspace MCP servers via Telegram
- **2-Way Conversations**: True chat with Claude, not just notifications
- **Workspace Context**: Automatically loads CLAUDE.md for project knowledge
- **Conversation History**: Maintains context across messages
- **Tool Use Loop**: Claude can use multiple tools to complete complex tasks
- **Security**: Chat ID restriction, webhook secret validation

## Files

| File | Purpose |
|------|---------|
| `service.py` | Main FastAPI application |
| `mcp_client.py` | MCP protocol client for connecting to MCP servers |
| `config.py` | Pydantic settings configuration |
| `cli.py` | Management CLI for webhook setup, testing |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |
| `telegram-bridge.service` | Systemd unit file |

## Quick Start

### 1. Copy to Your Workspace

```bash
cp -r framework/packages/telegram-bridge workspace/services/
cd workspace/services/telegram-bridge
```

### 2. Set Up Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your values
```

Required variables:
- `TELEGRAM_BOT_TOKEN` - From @BotFather
- `TELEGRAM_CHAT_ID` - Your authorized chat ID
- `ANTHROPIC_API_KEY` - Claude API key
- `WORKSPACE_PATH` - Path to your workspace root

### 4. Create Telegram Bot

1. Message @BotFather on Telegram
2. Send `/newbot` and follow prompts
3. Copy the bot token to your `.env`

### 5. Get Your Chat ID

1. Message @userinfobot on Telegram
2. It will reply with your chat ID

### 6. Deploy Service

```bash
# Edit paths in service file
nano telegram-bridge.service

# Install systemd service
sudo cp telegram-bridge.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-bridge
sudo systemctl start telegram-bridge
```

### 7. Configure Reverse Proxy

Example Caddy configuration:

```caddy
your-domain.com {
    handle /telegram/* {
        uri strip_prefix /telegram
        reverse_proxy 127.0.0.1:8420
    }
}
```

### 8. Set Up Webhook

```bash
python cli.py setup-webhook --url "https://your-domain.com/telegram/webhook/telegram"
```

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with tool count |
| `/status` | MCP server status |
| `/tools` | List available tools |
| `/clear` | Clear conversation history |
| `/help` | Help message |

## MCP Integration

The bridge automatically reads your workspace `.mcp.json` and connects to all configured MCP servers.

### Excluding Servers

Some servers don't make sense for Telegram (browser automation, web scraping). Edit `mcp_client.py`:

```python
skip_servers = {"playwright", "firecrawl", "other-server"}
```

### Tool Naming

Tools are namespaced: `{server}__{tool_name}`

Example: `email__send_email`, `crm__list_contacts`

## Security

1. **Chat ID Restriction**: Only responds to the configured `TELEGRAM_CHAT_ID`
2. **Webhook Secret**: Validates incoming webhooks with secret token
3. **No Credentials in Code**: All secrets via environment variables

## Customization

### System Prompt

The default system prompt loads from `CLAUDE.md` in your workspace. Override with `SYSTEM_PROMPT_FILE`:

```bash
export SYSTEM_PROMPT_FILE=/path/to/custom/prompt.txt
```

### Conversation History

Adjust `MAX_HISTORY_LENGTH` in `service.py` (default: 20 messages).

### Claude Model

Change model in `.env`:

```bash
CLAUDE_MODEL=claude-sonnet-4-20250514  # or other models
```

## Monitoring

```bash
# Service status
sudo systemctl status telegram-bridge

# Live logs
sudo journalctl -u telegram-bridge -f

# Health check
curl https://your-domain.com/telegram/health
```

## Troubleshooting

### Bot not responding

1. Check service: `sudo systemctl status telegram-bridge`
2. Check logs: `sudo journalctl -u telegram-bridge -n 50`
3. Verify webhook: `python cli.py webhook-info`

### MCP servers not starting

1. Verify paths in workspace `.mcp.json`
2. Check MCP server virtual environments exist
3. Look for specific errors in logs

### Tool calls failing

1. Verify MCP server credentials
2. Test MCP servers independently
3. Check for API rate limits

---

*Part of the Claude Workspace Framework*
