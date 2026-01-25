# Build MCP Server

Step-by-step guide to building a custom MCP (Model Context Protocol) server for workspace integrations.

## Prerequisites

- [ ] Python 3.10+ installed
- [ ] UV package manager (`pip install uv`)
- [ ] API credentials for target service
- [ ] Understanding of target service's API

## Step 1: Create Server Directory

```bash
mkdir -p ~/mcp-servers/[service-name]-mcp
cd ~/mcp-servers/[service-name]-mcp
```

## Step 2: Initialize Project

```bash
# Create virtual environment
uv venv

# Activate
source .venv/bin/activate

# Install MCP SDK
uv pip install mcp anthropic httpx python-dotenv
```

## Step 3: Create Server Structure

```
[service-name]-mcp/
├── .venv/
├── .env                 # Credentials (gitignored)
├── .env.example         # Template for credentials
├── .gitignore
├── pyproject.toml
├── README.md
└── src/
    └── [service_name]_mcp/
        ├── __init__.py
        ├── server.py    # Main MCP server
        ├── client.py    # API client wrapper
        └── tools.py     # Tool definitions
```

## Step 4: Create pyproject.toml

```toml
[project]
name = "[service-name]-mcp"
version = "0.1.0"
description = "MCP server for [Service Name] integration"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
    "httpx>=0.27.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
[service-name]-mcp = "[service_name]_mcp.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Step 5: Create API Client

`src/[service_name]_mcp/client.py`:

```python
"""API client for [Service Name]."""

import httpx
from typing import Any


class ServiceClient:
    """Client for [Service Name] API."""

    def __init__(self, api_key: str, base_url: str = "https://api.service.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def list_items(self, limit: int = 50) -> list[dict[str, Any]]:
        """List items from the service."""
        response = await self.client.get("/items", params={"limit": limit})
        response.raise_for_status()
        return response.json()

    async def get_item(self, item_id: str) -> dict[str, Any]:
        """Get a specific item."""
        response = await self.client.get(f"/items/{item_id}")
        response.raise_for_status()
        return response.json()

    async def create_item(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new item."""
        response = await self.client.post("/items", json=data)
        response.raise_for_status()
        return response.json()

    async def update_item(self, item_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing item."""
        response = await self.client.patch(f"/items/{item_id}", json=data)
        response.raise_for_status()
        return response.json()

    async def delete_item(self, item_id: str) -> bool:
        """Delete an item."""
        response = await self.client.delete(f"/items/{item_id}")
        response.raise_for_status()
        return True

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
```

## Step 6: Define Tools

`src/[service_name]_mcp/tools.py`:

```python
"""Tool definitions for [Service Name] MCP server."""

TOOLS = [
    {
        "name": "[service]_list",
        "description": "List items from [Service Name]",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of items to return",
                    "default": 50,
                },
                "filter": {
                    "type": "string",
                    "description": "Optional filter criteria",
                },
            },
            "required": [],
        },
    },
    {
        "name": "[service]_get",
        "description": "Get a specific item by ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The ID of the item to retrieve",
                },
            },
            "required": ["item_id"],
        },
    },
    {
        "name": "[service]_create",
        "description": "Create a new item",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the item",
                },
                "data": {
                    "type": "object",
                    "description": "Item data",
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "[service]_update",
        "description": "Update an existing item",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The ID of the item to update",
                },
                "data": {
                    "type": "object",
                    "description": "Updated item data",
                },
            },
            "required": ["item_id", "data"],
        },
    },
    {
        "name": "[service]_delete",
        "description": "Delete an item",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The ID of the item to delete",
                },
            },
            "required": ["item_id"],
        },
    },
]
```

## Step 7: Create Main Server

`src/[service_name]_mcp/server.py`:

```python
"""MCP server for [Service Name]."""

import os
import json
import asyncio
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import ServiceClient
from .tools import TOOLS

# Load environment variables
load_dotenv()

# Initialize server
server = Server("[service-name]-mcp")
client: ServiceClient | None = None


def get_client() -> ServiceClient:
    """Get or create the API client."""
    global client
    if client is None:
        api_key = os.getenv("[SERVICE]_API_KEY")
        if not api_key:
            raise ValueError("[SERVICE]_API_KEY environment variable required")
        client = ServiceClient(api_key)
    return client


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [Tool(**tool) for tool in TOOLS]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    api = get_client()

    try:
        if name == "[service]_list":
            result = await api.list_items(
                limit=arguments.get("limit", 50)
            )

        elif name == "[service]_get":
            result = await api.get_item(arguments["item_id"])

        elif name == "[service]_create":
            result = await api.create_item({
                "name": arguments["name"],
                **arguments.get("data", {}),
            })

        elif name == "[service]_update":
            result = await api.update_item(
                arguments["item_id"],
                arguments["data"]
            )

        elif name == "[service]_delete":
            await api.delete_item(arguments["item_id"])
            result = {"success": True, "message": "Item deleted"}

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def run():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """Entry point."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
```

## Step 8: Create Environment Files

`.env.example`:
```bash
# [Service Name] API credentials
[SERVICE]_API_KEY=your-api-key-here
[SERVICE]_BASE_URL=https://api.service.com
```

`.gitignore`:
```
.env
.venv/
__pycache__/
*.pyc
.DS_Store
```

## Step 9: Install and Test Locally

```bash
# Install in development mode
uv pip install -e .

# Test the server
python -m [service_name]_mcp.server
```

## Step 10: Add to Workspace .mcp.json

```json
{
  "mcpServers": {
    "[service-name]": {
      "command": "/path/to/[service-name]-mcp/.venv/bin/python",
      "args": ["-m", "[service_name]_mcp.server"],
      "env": {
        "[SERVICE]_API_KEY": "${[SERVICE]_API_KEY}"
      }
    }
  }
}
```

## Step 11: Test in Claude

```
# Verify tools are available
What [service] tools do you have access to?

# Test list
List items from [service]

# Test get
Get [service] item with ID "123"
```

## Common Patterns

### Pagination

```python
async def list_items_paginated(self, page: int = 1, per_page: int = 50):
    """List with pagination support."""
    response = await self.client.get("/items", params={
        "page": page,
        "per_page": per_page,
    })
    response.raise_for_status()
    data = response.json()
    return {
        "items": data["items"],
        "total": data["total"],
        "page": page,
        "pages": data["total_pages"],
    }
```

### Rate Limiting

```python
import asyncio
from datetime import datetime, timedelta

class RateLimitedClient:
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.requests = []

    async def _wait_for_rate_limit(self):
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        self.requests = [r for r in self.requests if r > minute_ago]

        if len(self.requests) >= self.rpm:
            sleep_time = (self.requests[0] - minute_ago).total_seconds()
            await asyncio.sleep(sleep_time)

        self.requests.append(now)
```

### Error Handling

```python
from httpx import HTTPStatusError

async def safe_request(self, method: str, path: str, **kwargs):
    """Make request with error handling."""
    try:
        response = await self.client.request(method, path, **kwargs)
        response.raise_for_status()
        return response.json()
    except HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        elif e.response.status_code == 429:
            # Rate limited - wait and retry
            await asyncio.sleep(60)
            return await self.safe_request(method, path, **kwargs)
        else:
            raise
```

## Troubleshooting

### Server Not Starting

1. Check Python version (3.10+)
2. Verify dependencies installed
3. Check .env file exists and has credentials

### Tools Not Appearing

1. Verify `list_tools()` returns correctly
2. Check tool schema format
3. Review MCP server logs

### API Errors

1. Check API key validity
2. Verify base URL
3. Test API directly with curl

## Next Steps

- [ ] Add more tools as needed
- [ ] Implement caching for frequent requests
- [ ] Add logging for debugging
- [ ] Create resources for static data
- [ ] Document tool usage in skills

---

*Playbook version: 1.0.0*
