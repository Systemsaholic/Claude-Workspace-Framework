# MCP Server Catalog

Catalog of available MCP servers that can be selectively deployed to workspaces.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  MCP Servers Repo (Systemsaholic/mcp-servers)               │
│  ├── cpanel-mcp/     (code only, no credentials)            │
│  ├── email-mcp/                                             │
│  ├── telegram-mcp/                                          │
│  └── ...                                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ deploy-mcp.sh install
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Your Workspace                                             │
│  ├── .env                 (YOUR credentials - gitignored)   │
│  ├── .mcp.json            (MCP configuration)               │
│  └── mcp-servers/                                           │
│      └── cpanel-mcp/      (installed from catalog)          │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# List available MCPs
./framework/scripts/deploy-mcp.sh list

# Get info about an MCP
./framework/scripts/deploy-mcp.sh info cpanel-mcp

# Install MCPs you need
./framework/scripts/deploy-mcp.sh install cpanel-mcp telegram-mcp

# Configure credentials
cp mcp-servers/cpanel-mcp/.env.example mcp-servers/cpanel-mcp/.env
# Edit .env with your credentials

# Add to .mcp.json
```

## Credential Management

**Credentials are NEVER stored in:**
- The framework repo
- The MCP servers repo
- Git history

**Credentials ARE stored in:**
- Workspace `.env` files (gitignored)
- Environment variables
- Secret managers (Vaultwarden, 1Password, etc.)

### .env File Pattern

Each MCP has a `.env.example` showing required variables:

```bash
# mcp-servers/cpanel-mcp/.env.example
CPANEL_WHM_URL=https://server.example.com:2087
CPANEL_API_TOKEN=your-token-here
CPANEL_USERNAME=root
```

Copy to `.env` and fill in real values:

```bash
cp mcp-servers/cpanel-mcp/.env.example mcp-servers/cpanel-mcp/.env
```

### .mcp.json Configuration

After installing, add the MCP to your `.mcp.json`:

```json
{
  "cpanel": {
    "command": "./mcp-servers/cpanel-mcp/.venv/bin/python",
    "args": ["-m", "cpanel_mcp"],
    "cwd": "./mcp-servers/cpanel-mcp",
    "env": {
      "CPANEL_WHM_URL": "${CPANEL_WHM_URL}",
      "CPANEL_API_TOKEN": "${CPANEL_API_TOKEN}",
      "CPANEL_USERNAME": "${CPANEL_USERNAME}"
    }
  }
}
```

Or source from the MCP's `.env` file directly in your shell.

## Available MCPs

| Category | MCP | Description |
|----------|-----|-------------|
| **Infrastructure** | cpanel-mcp | cPanel/WHM server management |
| **Communication** | email-mcp | IMAP/SMTP email |
| | telegram-mcp | Telegram notifications |
| **CRM** | groundhogg-mcp | WordPress CRM |
| **Productivity** | nextcloud-mcp | Files and calendar |
| **Secrets** | vaultwarden-mcp | Password manager |
| **Documents** | docuseal-mcp | E-signatures |

See `index.yaml` for full catalog with requirements.

## Adding New MCPs

1. Create MCP in the `mcp-servers` repo
2. Add entry to `mcp-catalog/index.yaml`
3. Include `.env.example` with required variables
4. Push both repos

## Security Notes

- Never commit `.env` files
- Use environment variables in CI/CD
- Consider secret managers for production
- Rotate API keys regularly
- Each workspace should have unique credentials where possible
