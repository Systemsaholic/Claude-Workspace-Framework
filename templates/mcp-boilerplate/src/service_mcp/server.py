"""MCP server for Service.

This is the main entry point for the MCP server. It handles:
- Server initialization
- Tool listing
- Tool execution
- Error handling

Run with: python -m service_mcp.server
"""

import os
import json
import asyncio
import logging
from typing import Any
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import ServiceClient, ServiceConfig
from .tools import TOOLS

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("SERVICE_DEBUG") else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("service-mcp")

# Initialize MCP server
server = Server("service-mcp")

# Global client instance (lazy initialization)
_client: ServiceClient | None = None


def get_client() -> ServiceClient:
    """Get or create the API client.

    Returns:
        Configured ServiceClient instance

    Raises:
        ValueError: If required environment variables are missing
    """
    global _client

    if _client is None:
        api_key = os.getenv("SERVICE_API_KEY")
        if not api_key:
            raise ValueError(
                "SERVICE_API_KEY environment variable is required. "
                "Set it in .env file or environment."
            )

        config = ServiceConfig(
            api_key=api_key,
            base_url=os.getenv("SERVICE_BASE_URL", "https://api.service.com"),
            timeout=float(os.getenv("SERVICE_TIMEOUT", "30")),
        )

        _client = ServiceClient(config)
        logger.info(f"Initialized client for {config.base_url}")

    return _client


def format_result(data: Any) -> str:
    """Format API result for display.

    Args:
        data: API response data

    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=2, default=str)


def format_error(error: Exception) -> str:
    """Format error for display.

    Args:
        error: Exception that occurred

    Returns:
        Formatted error message
    """
    return f"Error: {type(error).__name__}: {str(error)}"


# -----------------------------------------------------------------------------
# MCP Handlers
# -----------------------------------------------------------------------------

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools.

    Called by Claude to discover what tools this server provides.

    Returns:
        List of Tool objects with schemas
    """
    logger.debug(f"Listing {len(TOOLS)} tools")
    return [Tool(**tool) for tool in TOOLS]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from Claude.

    Args:
        name: Name of the tool to call
        arguments: Tool arguments from Claude

    Returns:
        List containing TextContent with result
    """
    logger.info(f"Tool call: {name} with args: {arguments}")

    try:
        client = get_client()
        result = await _execute_tool(client, name, arguments)

        return [TextContent(
            type="text",
            text=format_result(result),
        )]

    except Exception as e:
        logger.error(f"Tool {name} failed: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=format_error(e),
        )]


async def _execute_tool(
    client: ServiceClient,
    name: str,
    args: dict,
) -> Any:
    """Execute a specific tool.

    Args:
        client: API client instance
        name: Tool name
        args: Tool arguments

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool name is unknown
    """
    # -------------------------------------------------------------------------
    # List
    # -------------------------------------------------------------------------
    if name == "service_list":
        return await client.list_items(
            limit=args.get("limit", 50),
            offset=args.get("offset", 0),
            filter_status=args.get("status"),
        )

    # -------------------------------------------------------------------------
    # Get
    # -------------------------------------------------------------------------
    elif name == "service_get":
        return await client.get_item(args["item_id"])

    # -------------------------------------------------------------------------
    # Create
    # -------------------------------------------------------------------------
    elif name == "service_create":
        data = {
            "name": args["name"],
        }
        if "description" in args:
            data["description"] = args["description"]
        if "status" in args:
            data["status"] = args["status"]
        if "metadata" in args:
            data["metadata"] = args["metadata"]

        return await client.create_item(data)

    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------
    elif name == "service_update":
        data = {}
        for field in ["name", "description", "status", "metadata"]:
            if field in args:
                data[field] = args[field]

        return await client.update_item(args["item_id"], data)

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------
    elif name == "service_delete":
        if not args.get("confirm"):
            return {"error": "Deletion must be confirmed with confirm=true"}

        return await client.delete_item(args["item_id"])

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------
    elif name == "service_search":
        return await client.search_items(
            query=args["query"],
            limit=args.get("limit", 20),
        )

    # -------------------------------------------------------------------------
    # Unknown
    # -------------------------------------------------------------------------
    else:
        raise ValueError(f"Unknown tool: {name}")


# -----------------------------------------------------------------------------
# Server Lifecycle
# -----------------------------------------------------------------------------

async def run():
    """Run the MCP server.

    Starts the stdio-based MCP server and handles communication
    with Claude.
    """
    logger.info("Starting Service MCP server")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    """Entry point for the MCP server."""
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
