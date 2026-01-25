"""WHM server-level tools."""

import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from ..client import CpanelClient

logger = logging.getLogger(__name__)


def register_server_tools(mcp: FastMCP) -> None:
    """Register WHM server tools with the MCP server."""

    @mcp.tool()
    async def server_status() -> dict:
        """
        Check cPanel/WHM server status and connection health.

        Returns:
            Dictionary with server info and connection status.
        """
        async with CpanelClient() as client:
            # Get server version info
            try:
                version_info = await client.whm_api("version")
                version = version_info.get("data", {}).get("version", "unknown")
            except Exception:
                version = "unknown"

            # Get load averages
            try:
                load_info = await client.whm_api("loadavg")
                load = load_info.get("data", {})
            except Exception:
                load = {}

            # Count accounts
            try:
                accounts_info = await client.whm_api("listaccts")
                account_count = len(accounts_info.get("data", {}).get("acct", []))
            except Exception:
                account_count = -1

            return {
                "status": "connected",
                "url": client.config.whm_url,
                "version": version,
                "load_average": load,
                "account_count": account_count,
            }

    @mcp.tool()
    async def get_server_load() -> dict:
        """
        Get server load averages and system info.

        Returns:
            Dictionary with load averages and uptime info.
        """
        async with CpanelClient() as client:
            load_info = await client.whm_api("loadavg")
            return {
                "load_1min": load_info.get("data", {}).get("one", 0),
                "load_5min": load_info.get("data", {}).get("five", 0),
                "load_15min": load_info.get("data", {}).get("fifteen", 0),
            }

    @mcp.tool()
    async def get_disk_usage() -> dict:
        """
        Get disk usage information for the server.

        Returns:
            Dictionary with disk usage by partition.
        """
        async with CpanelClient() as client:
            # getdiskusage returns disk space info
            disk_info = await client.whm_api("getdiskusage")
            return {
                "partitions": disk_info.get("data", {}),
            }

    @mcp.tool()
    async def list_services() -> dict:
        """
        List status of server services.

        Returns:
            Dictionary with service status information.
        """
        async with CpanelClient() as client:
            services_info = await client.whm_api("servicestatus")
            services = services_info.get("data", {}).get("service", [])

            # Format service list
            formatted = []
            for svc in services:
                formatted.append({
                    "name": svc.get("name", "unknown"),
                    "running": svc.get("running", False),
                    "enabled": svc.get("enabled", False),
                })

            return {
                "services": formatted,
                "count": len(formatted),
            }

    @mcp.tool()
    async def restart_service(service_name: str) -> dict:
        """
        Restart a server service.

        Args:
            service_name: Name of service to restart (e.g., 'httpd', 'mysql', 'exim')

        Returns:
            Dictionary with restart result.
        """
        async with CpanelClient() as client:
            result = await client.whm_api(
                "restartservice",
                params={"service": service_name}
            )
            return {
                "service": service_name,
                "restarted": True,
                "result": result.get("data", {}),
            }

    @mcp.tool()
    async def get_bandwidth_usage(
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> dict:
        """
        Get server bandwidth usage statistics.

        Args:
            year: Year for stats (default: current year)
            month: Month for stats (default: current month)

        Returns:
            Dictionary with bandwidth usage data.
        """
        async with CpanelClient() as client:
            params = {}
            if year:
                params["year"] = year
            if month:
                params["month"] = month

            bw_info = await client.whm_api("showbw", params=params)
            return {
                "bandwidth": bw_info.get("data", {}),
            }

    logger.info("Registered WHM server tools")
