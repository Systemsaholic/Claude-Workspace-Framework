"""cPanel/WHM MCP tools."""

from .accounts import register_account_tools
from .domains import register_domain_tools
from .server import register_server_tools

__all__ = [
    "register_account_tools",
    "register_domain_tools",
    "register_server_tools",
]
