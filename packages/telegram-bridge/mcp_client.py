"""
MCP Client - Connects to MCP servers and exposes tools for Claude.

This module handles:
1. Loading MCP server configurations from .mcp.json
2. Starting MCP server processes
3. Communicating via MCP protocol (JSON-RPC over stdio)
4. Converting tools to Anthropic API format
"""

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("telegram-bridge.mcp")


class MCPServerConnection:
    """Manages connection to a single MCP server."""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.tools: list[dict] = []
        self.request_id = 0
        self._lock = asyncio.Lock()

    async def start(self) -> bool:
        """Start the MCP server process."""
        try:
            command = self.config.get("command")
            args = self.config.get("args", [])
            cwd = self.config.get("cwd")
            env_vars = self.config.get("env", {})

            # Build environment
            env = os.environ.copy()
            env.update(env_vars)

            # Build full command
            full_command = [command] + args

            logger.info(f"Starting MCP server '{self.name}': {' '.join(full_command)}")

            self.process = subprocess.Popen(
                full_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=env,
                text=True,
                bufsize=1,
            )

            # Initialize the connection
            await self._initialize()
            return True

        except Exception as e:
            logger.error(f"Failed to start MCP server '{self.name}': {e}")
            return False

    async def _initialize(self) -> None:
        """Initialize MCP connection and get tools."""
        # Send initialize request
        init_response = await self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "telegram-bridge",
                "version": "1.0.0"
            }
        })

        if init_response:
            logger.info(f"MCP server '{self.name}' initialized")

            # Send initialized notification
            await self._send_notification("notifications/initialized", {})

            # Get available tools
            tools_response = await self._send_request("tools/list", {})
            if tools_response and "tools" in tools_response:
                self.tools = tools_response["tools"]
                logger.info(f"MCP server '{self.name}' has {len(self.tools)} tools")

    async def _send_request(self, method: str, params: dict) -> Optional[dict]:
        """Send a JSON-RPC request and wait for response."""
        if not self.process or not self.process.stdin or not self.process.stdout:
            return None

        async with self._lock:
            self.request_id += 1
            request = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": method,
                "params": params
            }

            try:
                # Send request
                request_line = json.dumps(request) + "\n"
                self.process.stdin.write(request_line)
                self.process.stdin.flush()

                # Read response (with timeout)
                loop = asyncio.get_event_loop()
                response_line = await asyncio.wait_for(
                    loop.run_in_executor(None, self.process.stdout.readline),
                    timeout=30.0
                )

                if response_line:
                    response = json.loads(response_line)
                    if "result" in response:
                        return response["result"]
                    elif "error" in response:
                        logger.error(f"MCP error from '{self.name}': {response['error']}")

            except asyncio.TimeoutError:
                logger.error(f"Timeout waiting for response from '{self.name}'")
            except Exception as e:
                logger.error(f"Error communicating with '{self.name}': {e}")

            return None

    async def _send_notification(self, method: str, params: dict) -> None:
        """Send a JSON-RPC notification (no response expected)."""
        if not self.process or not self.process.stdin:
            return

        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }

        try:
            notification_line = json.dumps(notification) + "\n"
            self.process.stdin.write(notification_line)
            self.process.stdin.flush()
        except Exception as e:
            logger.error(f"Error sending notification to '{self.name}': {e}")

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a tool on this MCP server."""
        response = await self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

        if response and "content" in response:
            # Extract text content
            content_parts = []
            for item in response["content"]:
                if item.get("type") == "text":
                    content_parts.append(item.get("text", ""))
            return "\n".join(content_parts)

        return response

    def stop(self) -> None:
        """Stop the MCP server process."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None

    def get_anthropic_tools(self) -> list[dict]:
        """Convert MCP tools to Anthropic API format."""
        anthropic_tools = []
        for tool in self.tools:
            anthropic_tool = {
                "name": f"{self.name}__{tool['name']}",
                "description": f"[{self.name}] {tool.get('description', '')}",
                "input_schema": tool.get("inputSchema", {"type": "object", "properties": {}})
            }
            anthropic_tools.append(anthropic_tool)
        return anthropic_tools


class MCPManager:
    """Manages multiple MCP server connections."""

    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.servers: dict[str, MCPServerConnection] = {}
        self._started = False

    def load_config(self) -> dict:
        """Load MCP configuration from .mcp.json."""
        if not self.config_path:
            # Try to get from settings
            from config import get_settings
            self.config_path = get_settings().mcp_json_path

        config_file = Path(self.config_path)
        if not config_file.exists():
            logger.warning(f"MCP config not found: {self.config_path}")
            return {}

        with open(config_file) as f:
            config = json.load(f)

        return config.get("mcpServers", {})

    async def start_servers(self, server_names: list[str] = None) -> None:
        """Start MCP servers."""
        if self._started:
            return

        config = self.load_config()

        # Filter to specific servers if requested
        if server_names:
            config = {k: v for k, v in config.items() if k in server_names}

        # Skip servers that don't make sense for Telegram chat
        # Customize this list based on your workspace
        skip_servers = {"playwright", "context7", "firecrawl"}
        config = {k: v for k, v in config.items() if k not in skip_servers}

        for name, server_config in config.items():
            server = MCPServerConnection(name, server_config)
            if await server.start():
                self.servers[name] = server
            else:
                logger.warning(f"Failed to start MCP server: {name}")

        self._started = True
        logger.info(f"Started {len(self.servers)} MCP servers")

    def stop_servers(self) -> None:
        """Stop all MCP servers."""
        for server in self.servers.values():
            server.stop()
        self.servers.clear()
        self._started = False

    def get_all_tools(self) -> list[dict]:
        """Get all tools from all servers in Anthropic format."""
        all_tools = []
        for server in self.servers.values():
            all_tools.extend(server.get_anthropic_tools())
        return all_tools

    async def call_tool(self, full_tool_name: str, arguments: dict) -> Any:
        """Call a tool by its full name (server__toolname)."""
        if "__" not in full_tool_name:
            return f"Invalid tool name format: {full_tool_name}"

        server_name, tool_name = full_tool_name.split("__", 1)

        if server_name not in self.servers:
            return f"Server not found: {server_name}"

        server = self.servers[server_name]
        return await server.call_tool(tool_name, arguments)

    def get_server_status(self) -> dict:
        """Get status of all servers."""
        return {
            name: {
                "running": server.process is not None and server.process.poll() is None,
                "tools_count": len(server.tools)
            }
            for name, server in self.servers.items()
        }
