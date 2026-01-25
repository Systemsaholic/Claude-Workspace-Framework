# Service MCP Server

MCP (Model Context Protocol) server for integrating with Service.

## Setup

1. Clone or copy this directory
2. Create virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

4. Configure credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

## Usage

### Run standalone

```bash
python -m service_mcp.server
```

### Add to Claude Code

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "service": {
      "command": "/path/to/service-mcp/.venv/bin/python",
      "args": ["-m", "service_mcp.server"],
      "env": {
        "SERVICE_API_KEY": "${SERVICE_API_KEY}"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `service_list` | List items |
| `service_get` | Get item by ID |
| `service_create` | Create new item |
| `service_update` | Update existing item |
| `service_delete` | Delete item |
| `service_search` | Search items |

## Development

### Add new tool

1. Define tool schema in `src/service_mcp/tools.py`
2. Add handler in `src/service_mcp/server.py`
3. Add API method in `src/service_mcp/client.py`

### Test locally

```bash
# Run server in debug mode
SERVICE_DEBUG=true python -m service_mcp.server
```

## License

MIT
