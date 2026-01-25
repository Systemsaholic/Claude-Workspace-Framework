"""WHM account management tools."""

import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from ..client import CpanelClient

logger = logging.getLogger(__name__)


def register_account_tools(mcp: FastMCP) -> None:
    """Register WHM account management tools with the MCP server."""

    @mcp.tool()
    async def list_accounts(
        search: Optional[str] = None,
        search_type: str = "domain"
    ) -> dict:
        """
        List all cPanel accounts on the server.

        Args:
            search: Optional search term
            search_type: Field to search: 'domain', 'user', 'owner', 'ip', 'package'

        Returns:
            Dictionary with list of accounts.
        """
        async with CpanelClient() as client:
            params = {}
            if search:
                params["search"] = search
                params["searchtype"] = search_type

            result = await client.whm_api("listaccts", params=params)
            accounts = result.get("data", {}).get("acct", [])

            # Format account list
            formatted = []
            for acct in accounts:
                formatted.append({
                    "user": acct.get("user"),
                    "domain": acct.get("domain"),
                    "email": acct.get("email"),
                    "plan": acct.get("plan"),
                    "suspended": acct.get("suspended", False),
                    "disk_used": acct.get("diskused"),
                    "disk_limit": acct.get("disklimit"),
                    "ip": acct.get("ip"),
                    "owner": acct.get("owner"),
                    "created": acct.get("startdate"),
                })

            return {
                "accounts": formatted,
                "count": len(formatted),
            }

    @mcp.tool()
    async def get_account_info(username: str) -> dict:
        """
        Get detailed information about a cPanel account.

        Args:
            username: cPanel account username

        Returns:
            Dictionary with account details.
        """
        async with CpanelClient() as client:
            result = await client.whm_api(
                "accountsummary",
                params={"user": username}
            )
            acct = result.get("data", {}).get("acct", [{}])[0]

            return {
                "user": acct.get("user"),
                "domain": acct.get("domain"),
                "email": acct.get("email"),
                "plan": acct.get("plan"),
                "suspended": acct.get("suspended", False),
                "suspend_reason": acct.get("suspendreason"),
                "disk_used": acct.get("diskused"),
                "disk_limit": acct.get("disklimit"),
                "ip": acct.get("ip"),
                "dedicated_ip": acct.get("ip") if acct.get("iptype") == "dedicated" else None,
                "owner": acct.get("owner"),
                "shell": acct.get("shell"),
                "max_addons": acct.get("maxaddons"),
                "max_parked": acct.get("maxparked"),
                "max_ftp": acct.get("maxftp"),
                "max_sql": acct.get("maxsql"),
                "max_pop": acct.get("maxpop"),
                "max_lists": acct.get("maxlists"),
                "created": acct.get("startdate"),
            }

    @mcp.tool()
    async def get_account_disk_usage(username: str) -> dict:
        """
        Get disk usage breakdown for a cPanel account.

        Args:
            username: cPanel account username

        Returns:
            Dictionary with disk usage by directory.
        """
        async with CpanelClient() as client:
            result = await client.whm_api(
                "getdiskusage",
                params={"user": username}
            )
            return {
                "user": username,
                "usage": result.get("data", {}),
            }

    @mcp.tool()
    async def suspend_account(
        username: str,
        reason: str = "Administrative action"
    ) -> dict:
        """
        Suspend a cPanel account.

        Args:
            username: cPanel account username
            reason: Reason for suspension

        Returns:
            Dictionary with suspension result.
        """
        async with CpanelClient() as client:
            result = await client.whm_api(
                "suspendacct",
                params={"user": username, "reason": reason}
            )
            return {
                "user": username,
                "suspended": True,
                "reason": reason,
                "result": result.get("data", {}),
            }

    @mcp.tool()
    async def unsuspend_account(username: str) -> dict:
        """
        Unsuspend a cPanel account.

        Args:
            username: cPanel account username

        Returns:
            Dictionary with unsuspension result.
        """
        async with CpanelClient() as client:
            result = await client.whm_api(
                "unsuspendacct",
                params={"user": username}
            )
            return {
                "user": username,
                "suspended": False,
                "result": result.get("data", {}),
            }

    @mcp.tool()
    async def change_account_password(
        username: str,
        password: str
    ) -> dict:
        """
        Change password for a cPanel account.

        Args:
            username: cPanel account username
            password: New password (should be strong)

        Returns:
            Dictionary with password change result.
        """
        async with CpanelClient() as client:
            result = await client.whm_api(
                "passwd",
                params={"user": username, "password": password}
            )
            return {
                "user": username,
                "password_changed": True,
                "result": result.get("data", {}),
            }

    @mcp.tool()
    async def modify_account(
        username: str,
        disk_limit: Optional[str] = None,
        bw_limit: Optional[str] = None,
        max_email: Optional[int] = None,
        max_ftp: Optional[int] = None,
        max_sql: Optional[int] = None,
    ) -> dict:
        """
        Modify a cPanel account's limits.

        Args:
            username: cPanel account username
            disk_limit: Disk quota (e.g., '5000M', 'unlimited')
            bw_limit: Bandwidth limit (e.g., '100000M', 'unlimited')
            max_email: Max email accounts
            max_ftp: Max FTP accounts
            max_sql: Max SQL databases

        Returns:
            Dictionary with modification result.
        """
        async with CpanelClient() as client:
            params = {"user": username}

            if disk_limit:
                params["QUOTA"] = disk_limit
            if bw_limit:
                params["BWLIMIT"] = bw_limit
            if max_email is not None:
                params["MAXPOP"] = max_email
            if max_ftp is not None:
                params["MAXFTP"] = max_ftp
            if max_sql is not None:
                params["MAXSQL"] = max_sql

            result = await client.whm_api("modifyacct", params=params)
            return {
                "user": username,
                "modified": True,
                "changes": {k: v for k, v in params.items() if k != "user"},
                "result": result.get("data", {}),
            }

    @mcp.tool()
    async def list_suspended_accounts() -> dict:
        """
        List all suspended cPanel accounts.

        Returns:
            Dictionary with list of suspended accounts.
        """
        async with CpanelClient() as client:
            result = await client.whm_api("listsuspended")
            accounts = result.get("data", {}).get("acct", [])

            formatted = []
            for acct in accounts:
                formatted.append({
                    "user": acct.get("user"),
                    "reason": acct.get("reason"),
                    "time": acct.get("time"),
                })

            return {
                "suspended_accounts": formatted,
                "count": len(formatted),
            }

    logger.info("Registered WHM account tools")
