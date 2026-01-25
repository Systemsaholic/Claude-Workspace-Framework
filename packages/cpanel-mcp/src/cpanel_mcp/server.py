"""cPanel/WHM MCP Server - Server management for AI assistants."""

import logging
import sys

from mcp.server.fastmcp import FastMCP

from .config import init_config
from .tools.server import register_server_tools
from .tools.accounts import register_account_tools
from .tools.domains import register_domain_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP(
    name="cpanel",
    instructions="""cPanel/WHM MCP Server for web hosting management.

This server provides tools to manage cPanel/WHM servers including:

- Server status and monitoring (load, disk, services)
- Account management (list, create, suspend, modify)
- Domain management (primary, addon, subdomains)
- DNS zone management (records, zones)
- SSL certificate management

Common workflows:
1. Check server status: server_status()
2. List accounts: list_accounts()
3. Get account info: get_account_info(username="example")
4. List domains: list_domains()
5. Check DNS: get_dns_zone(domain="example.com")
6. Check SSL: check_domain_ssl(domain="example.com")

Note: This connects to WHM API port 2087. Requires WHM API token.
""",
)


def register_all_tools() -> None:
    """Register all tools with the MCP server."""
    logger.info("Registering cPanel/WHM MCP tools...")

    register_server_tools(mcp)
    register_account_tools(mcp)
    register_domain_tools(mcp)

    logger.info("All tools registered successfully")


def main() -> None:
    """Main entry point for the cPanel/WHM MCP server."""
    try:
        # Initialize configuration from environment
        config = init_config()
        logger.info(f"cPanel/WHM MCP server starting - URL: {config.whm_url}")

        # Register all tools
        register_all_tools()

        # Run the server with stdio transport
        logger.info("Starting MCP server with stdio transport...")
        mcp.run(transport="stdio")

    except Exception as e:
        logger.error(f"Failed to start cPanel/WHM MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
