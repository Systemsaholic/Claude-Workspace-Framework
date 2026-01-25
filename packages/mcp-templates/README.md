# MCP Templates Package

Boilerplate and patterns for building Model Context Protocol servers.

## Overview

MCP servers bridge Claude to external systems:
- **Python MCP** - Most common, using `mcp` library
- **TypeScript MCP** - For Node.js ecosystems
- **NPX MCP** - Pre-built community servers

## MCP Server Types

### By Implementation

| Type | Language | Use Case |
|------|----------|----------|
| Python MCP | Python | Custom APIs, most flexibility |
| TypeScript MCP | Node.js | JS ecosystems, npm packages |
| NPX MCP | Any | Pre-built community servers |

### By Function

| Category | Examples |
|----------|----------|
| **Communication** | Email, Slack, Telegram, SMS |
| **Data/Storage** | Database, CRM, Spreadsheets |
| **Infrastructure** | Servers, DNS, Monitoring |
| **Productivity** | Calendar, Tasks, Documents |
| **Business** | Accounting, Billing, CRM |

## Python MCP Server Template

### Project Structure

```
my-mcp-server/
├── src/
│   └── my_mcp/
│       ├── __init__.py
│       ├── server.py       # Main MCP server
│       ├── tools.py        # Tool definitions
│       └── client.py       # API client wrapper
├── pyproject.toml
├── requirements.txt
├── README.md
└── .env.example
```

### Minimal Server (server.py)

```python
"""
My MCP Server - Brief description

Provides tools for [purpose].
"""

import os
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize server
server = Server("my-mcp-server")

# Environment configuration
API_KEY = os.environ.get("MY_API_KEY")
BASE_URL = os.environ.get("MY_BASE_URL", "https://api.example.com")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="my_tool",
            description="Does something useful",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "First parameter"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Second parameter (optional)",
                        "default": 10
                    }
                },
                "required": ["param1"]
            }
        ),
        Tool(
            name="another_tool",
            description="Does another thing",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool."""

    if name == "my_tool":
        param1 = arguments["param1"]
        param2 = arguments.get("param2", 10)

        # Do something
        result = f"Processed {param1} with {param2}"

        return [TextContent(type="text", text=result)]

    elif name == "another_tool":
        query = arguments["query"]

        # Do something else
        result = f"Found results for: {query}"

        return [TextContent(type="text", text=result)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Requirements (requirements.txt)

```
mcp>=0.9.0
httpx>=0.25.0
python-dotenv>=1.0.0
```

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-mcp-server"
version = "0.1.0"
description = "MCP server for [purpose]"
requires-python = ">=3.10"
dependencies = [
    "mcp>=0.9.0",
    "httpx>=0.25.0",
]

[project.scripts]
my-mcp = "my_mcp.server:main"
```

### .mcp.json Configuration

```json
{
  "my-mcp": {
    "command": "/path/to/my-mcp-server/.venv/bin/python",
    "args": ["-m", "my_mcp.server"],
    "cwd": "/path/to/my-mcp-server",
    "env": {
      "MY_API_KEY": "your-api-key",
      "MY_BASE_URL": "https://api.example.com"
    }
  }
}
```

## Common MCP Patterns

### API Client Pattern

```python
# client.py
import httpx
from typing import Optional

class MyAPIClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"}
        )

    async def get_items(self, limit: int = 10) -> list:
        response = await self.client.get("/items", params={"limit": limit})
        response.raise_for_status()
        return response.json()

    async def create_item(self, data: dict) -> dict:
        response = await self.client.post("/items", json=data)
        response.raise_for_status()
        return response.json()
```

### Confirmation Pattern

For destructive actions, require explicit confirmation:

```python
Tool(
    name="delete_item",
    description="Delete an item. Requires confirm=True.",
    inputSchema={
        "type": "object",
        "properties": {
            "item_id": {"type": "string"},
            "confirm": {
                "type": "boolean",
                "description": "Must be True to proceed"
            }
        },
        "required": ["item_id", "confirm"]
    }
)

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "delete_item":
        if not arguments.get("confirm"):
            return [TextContent(
                type="text",
                text="⚠️ This will delete the item. Set confirm=True to proceed."
            )]
        # Proceed with deletion
```

### Server Status Pattern

Every MCP should have a status check:

```python
Tool(
    name="server_status",
    description="Check MCP server connection and status",
    inputSchema={"type": "object", "properties": {}}
)

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "server_status":
        # Test API connection
        try:
            # Make test request
            status = "Connected"
            details = "API responding normally"
        except Exception as e:
            status = "Error"
            details = str(e)

        return [TextContent(
            type="text",
            text=f"Status: {status}\n{details}"
        )]
```

## Plausible MCP Servers

### Communication

| MCP Server | Purpose | API |
|------------|---------|-----|
| **email-mcp** | IMAP/SMTP email | IMAP/SMTP |
| **gmail-mcp** | Google Workspace | Google API |
| **slack-mcp** | Slack messaging | Slack API |
| **telegram-mcp** | Telegram bot | Telegram Bot API |
| **twilio-mcp** | SMS/Voice | Twilio API |
| **discord-mcp** | Discord bot | Discord API |

### CRM / Marketing

| MCP Server | Purpose | API |
|------------|---------|-----|
| **groundhogg-mcp** | WordPress CRM | Groundhogg REST API |
| **hubspot-mcp** | HubSpot CRM | HubSpot API |
| **mailchimp-mcp** | Email marketing | Mailchimp API |
| **later-mcp** | Social scheduling | Later.dev API |
| **buffer-mcp** | Social media | Buffer API |

### Productivity

| MCP Server | Purpose | API |
|------------|---------|-----|
| **google-calendar-mcp** | Calendar | Google Calendar API |
| **notion-mcp** | Notion workspace | Notion API |
| **todoist-mcp** | Task management | Todoist API |
| **nextcloud-mcp** | File storage | Nextcloud API |
| **outline-mcp** | Wiki/docs | Outline API |

### Business / Finance

| MCP Server | Purpose | API |
|------------|---------|-----|
| **quickbooks-mcp** | Accounting | QuickBooks API |
| **wave-mcp** | Invoicing | Wave GraphQL API |
| **stripe-mcp** | Payments | Stripe API |
| **xero-mcp** | Accounting | Xero API |

### Infrastructure

| MCP Server | Purpose | API |
|------------|---------|-----|
| **cloudflare-mcp** | DNS/CDN | Cloudflare API |
| **cpanel-mcp** | Web hosting | cPanel/WHM API |
| **docker-mcp** | Containers | Docker API |
| **aws-mcp** | AWS services | AWS SDK |
| **digitalocean-mcp** | Cloud servers | DO API |

### Passwords / Secrets

| MCP Server | Purpose | API |
|------------|---------|-----|
| **bitwarden-mcp** | Password manager | Bitwarden CLI |
| **vaultwarden-mcp** | Self-hosted Bitwarden | Bitwarden API |
| **1password-mcp** | 1Password | 1Password CLI |

### Documents / Signatures

| MCP Server | Purpose | API |
|------------|---------|-----|
| **docuseal-mcp** | E-signatures | Docuseal API |
| **docusign-mcp** | E-signatures | DocuSign API |
| **pandadoc-mcp** | Documents | PandaDoc API |

### Pre-built NPX MCPs

```json
{
  "playwright": {
    "command": "npx",
    "args": ["-y", "@playwright/mcp", "--headless"]
  },
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  },
  "firecrawl": {
    "command": "npx",
    "args": ["-y", "firecrawl-mcp"],
    "env": {"FIRECRAWL_API_KEY": "..."}
  },
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@anthropic/mcp-server-filesystem", "/path"]
  }
}
```

## Building an MCP Server

### Step-by-Step

1. **Research the API**
   - Authentication method (API key, OAuth, etc.)
   - Available endpoints
   - Rate limits
   - Response formats

2. **Design tools**
   - What operations are needed?
   - What parameters for each?
   - Which need confirmation?

3. **Create project structure**
   ```bash
   mkdir my-mcp-server
   cd my-mcp-server
   python -m venv .venv
   source .venv/bin/activate
   pip install mcp httpx
   ```

4. **Implement client wrapper**
   ```python
   # client.py - API interactions
   ```

5. **Implement MCP server**
   ```python
   # server.py - Tool definitions
   ```

6. **Test locally**
   ```bash
   python -m my_mcp.server
   ```

7. **Configure in .mcp.json**

8. **Test with Claude**

## Best Practices

1. **Always add server_status** - For connectivity testing
2. **Require confirmation** - For destructive actions
3. **Handle errors gracefully** - Return useful messages
4. **Log operations** - For debugging
5. **Document tools well** - Clear descriptions
6. **Version your MCP** - Track changes
7. **Secure credentials** - Use environment variables

---

*Package version: 1.0.0*
