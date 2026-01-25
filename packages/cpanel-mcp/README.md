# cPanel/WHM MCP Server

MCP (Model Context Protocol) server for managing cPanel/WHM web hosting servers through AI assistants like Claude.

## Features

### Server Management
- `server_status` - Check server connection and basic info
- `get_server_load` - Get CPU load averages
- `get_disk_usage` - Check disk space
- `list_services` - List service status
- `restart_service` - Restart a service
- `get_bandwidth_usage` - Get bandwidth statistics

### Account Management
- `list_accounts` - List all cPanel accounts
- `get_account_info` - Get detailed account information
- `get_account_disk_usage` - Check account disk usage
- `suspend_account` - Suspend an account
- `unsuspend_account` - Unsuspend an account
- `change_account_password` - Change account password
- `modify_account` - Modify account limits
- `list_suspended_accounts` - List suspended accounts

### Domain Management
- `list_domains` - List all domains
- `get_domain_info` - Get domain details
- `list_addon_domains` - List addon domains for account
- `list_subdomains` - List subdomains for account
- `get_dns_zone` - Get DNS records
- `add_dns_record` - Add DNS record
- `remove_dns_record` - Remove DNS record
- `list_ssl_certificates` - List SSL certs
- `check_domain_ssl` - Check SSL status for domain

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package
pip install -e .
```

## Configuration

Set environment variables or create `.env` file:

```bash
# WHM server URL (port 2087)
CPANEL_WHM_URL=https://server.example.com:2087

# WHM API token (generate in WHM > Development > Manage API Tokens)
CPANEL_API_TOKEN=your-api-token-here

# WHM username (usually root)
CPANEL_USERNAME=root

# Request timeout (seconds)
CPANEL_REQUEST_TIMEOUT=30

# Allow self-signed certs (set true for internal servers)
CPANEL_ALLOW_INSECURE=false
```

### Generating WHM API Token

1. Log into WHM as root
2. Go to **Development** > **Manage API Tokens**
3. Click **Generate Token**
4. Give it a name (e.g., "mcp-server")
5. Copy the token (shown only once)

## Usage

### Standalone Test

```bash
# Verify configuration
python -c "from cpanel_mcp.config import get_config; c = get_config(); print(f'URL: {c.whm_url}')"
```

### With Claude Code

Add to `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "cpanel": {
      "command": "/path/to/cpanel-mcp/.venv/bin/python",
      "args": ["-m", "cpanel_mcp"],
      "env": {
        "CPANEL_WHM_URL": "https://server.example.com:2087",
        "CPANEL_API_TOKEN": "your-api-token",
        "CPANEL_USERNAME": "root",
        "CPANEL_ALLOW_INSECURE": "true"
      }
    }
  }
}
```

### Example Commands

```
# Check server status
"Check cPanel server status"

# List all accounts
"List all cPanel accounts on the server"

# Get account info
"Get details for cPanel account 'example'"

# Check domain DNS
"Show DNS records for example.com"

# Check SSL certificate
"Is SSL enabled for example.com?"
```

## Security Notes

- Store API tokens securely (use environment variables, not files)
- Use HTTPS (port 2087) for all connections
- The API token has full WHM access - protect it accordingly
- Set `CPANEL_ALLOW_INSECURE=true` only for internal servers with self-signed certs

## API Reference

This server uses the WHM API:
- https://api.docs.cpanel.net/whm/introduction/

And cPanel UAPI for account-level operations:
- https://api.docs.cpanel.net/cpanel/introduction/
