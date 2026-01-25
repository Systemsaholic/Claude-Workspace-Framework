"""Tool definitions for Service MCP server.

Each tool definition includes:
- name: Unique identifier (convention: service_action)
- description: What the tool does (shown to Claude)
- inputSchema: JSON Schema for parameters

Customize these tools based on your service's capabilities.
"""

TOOLS = [
    # -------------------------------------------------------------------------
    # List Tool
    # -------------------------------------------------------------------------
    {
        "name": "service_list",
        "description": "List items from Service with optional filtering and pagination",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of items to return (default: 50, max: 100)",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 100,
                },
                "offset": {
                    "type": "integer",
                    "description": "Number of items to skip for pagination",
                    "default": 0,
                    "minimum": 0,
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status (active, inactive, archived)",
                    "enum": ["active", "inactive", "archived"],
                },
            },
            "required": [],
        },
    },

    # -------------------------------------------------------------------------
    # Get Tool
    # -------------------------------------------------------------------------
    {
        "name": "service_get",
        "description": "Get a specific item by its ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The unique identifier of the item",
                },
            },
            "required": ["item_id"],
        },
    },

    # -------------------------------------------------------------------------
    # Create Tool
    # -------------------------------------------------------------------------
    {
        "name": "service_create",
        "description": "Create a new item in Service",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the item (required)",
                },
                "description": {
                    "type": "string",
                    "description": "Optional description",
                },
                "status": {
                    "type": "string",
                    "description": "Initial status (default: active)",
                    "enum": ["active", "inactive"],
                    "default": "active",
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional custom fields",
                    "additionalProperties": True,
                },
            },
            "required": ["name"],
        },
    },

    # -------------------------------------------------------------------------
    # Update Tool
    # -------------------------------------------------------------------------
    {
        "name": "service_update",
        "description": "Update an existing item",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The ID of the item to update",
                },
                "name": {
                    "type": "string",
                    "description": "New name (optional)",
                },
                "description": {
                    "type": "string",
                    "description": "New description (optional)",
                },
                "status": {
                    "type": "string",
                    "description": "New status (optional)",
                    "enum": ["active", "inactive", "archived"],
                },
                "metadata": {
                    "type": "object",
                    "description": "Metadata fields to update (merged with existing)",
                    "additionalProperties": True,
                },
            },
            "required": ["item_id"],
        },
    },

    # -------------------------------------------------------------------------
    # Delete Tool
    # -------------------------------------------------------------------------
    {
        "name": "service_delete",
        "description": "Delete an item (this action is permanent)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "The ID of the item to delete",
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Confirm deletion (must be true)",
                },
            },
            "required": ["item_id", "confirm"],
        },
    },

    # -------------------------------------------------------------------------
    # Search Tool
    # -------------------------------------------------------------------------
    {
        "name": "service_search",
        "description": "Search items by query string",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (searches name and description)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results to return",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 50,
                },
            },
            "required": ["query"],
        },
    },
]


def get_tool_by_name(name: str) -> dict | None:
    """Get a tool definition by name.

    Args:
        name: Tool name to find

    Returns:
        Tool definition dict or None if not found
    """
    for tool in TOOLS:
        if tool["name"] == name:
            return tool
    return None
