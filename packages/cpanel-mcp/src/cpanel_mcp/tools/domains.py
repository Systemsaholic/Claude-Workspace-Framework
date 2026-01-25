"""WHM domain management tools."""

import logging
from typing import Optional

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from mcp.server.fastmcp import FastMCP

from ..client import CpanelClient

logger = logging.getLogger(__name__)


def register_domain_tools(mcp: FastMCP) -> None:
    """Register WHM domain management tools with the MCP server."""

    @mcp.tool()
    async def list_domains() -> dict:
        """
        List all domains across all accounts on the server.

        Returns:
            Dictionary with list of all domains.
        """
        async with CpanelClient() as client:
            result = await client.whm_api("listaccts")
            accounts = result.get("data", {}).get("acct", [])

            domains = []
            for acct in accounts:
                # Primary domain
                domains.append({
                    "domain": acct.get("domain"),
                    "user": acct.get("user"),
                    "type": "primary",
                    "ip": acct.get("ip"),
                })

            return {
                "domains": domains,
                "count": len(domains),
            }

    @mcp.tool()
    async def get_domain_info(domain: str) -> dict:
        """
        Get information about a specific domain.

        Args:
            domain: Domain name to look up

        Returns:
            Dictionary with domain information.
        """
        async with CpanelClient() as client:
            result = await client.whm_api("domainuserdata", params={"domain": domain})
            data = result.get("data", {}).get("userdata", {})

            return {
                "domain": domain,
                "user": data.get("user"),
                "documentroot": data.get("documentroot"),
                "ip": data.get("ip"),
                "port": data.get("port"),
                "ssl": data.get("ssl", False),
                "php_version": data.get("phpversion"),
                "server_admin": data.get("serveradmin"),
            }

    @mcp.tool()
    async def list_addon_domains(username: str) -> dict:
        """
        List addon domains for a cPanel account.

        Args:
            username: cPanel account username

        Returns:
            Dictionary with addon domains.
        """
        async with CpanelClient() as client:
            result = await client.cpanel_uapi(
                account=username,
                module="AddonDomain",
                function="listaddondomains"
            )
            domains = result.get("data", [])

            return {
                "user": username,
                "addon_domains": domains,
                "count": len(domains),
            }

    @mcp.tool()
    async def list_subdomains(username: str) -> dict:
        """
        List subdomains for a cPanel account.

        Args:
            username: cPanel account username

        Returns:
            Dictionary with subdomains.
        """
        async with CpanelClient() as client:
            result = await client.cpanel_uapi(
                account=username,
                module="SubDomain",
                function="listsubdomains"
            )
            domains = result.get("data", [])

            return {
                "user": username,
                "subdomains": domains,
                "count": len(domains),
            }

    @mcp.tool()
    async def get_dns_zone(domain: str) -> dict:
        """
        Get DNS zone records for a domain.

        Args:
            domain: Domain name

        Returns:
            Dictionary with DNS records.
        """
        async with CpanelClient() as client:
            result = await client.whm_api("dumpzone", params={"domain": domain})
            zone = result.get("data", {}).get("zone", [])

            records = []
            for record in zone:
                records.append({
                    "name": record.get("name"),
                    "type": record.get("type"),
                    "record": record.get("record"),
                    "ttl": record.get("ttl"),
                    "line": record.get("Line"),
                })

            return {
                "domain": domain,
                "records": records,
                "count": len(records),
            }

    @mcp.tool()
    async def add_dns_record(
        domain: str,
        name: str,
        record_type: str,
        value: str,
        ttl: int = 14400
    ) -> dict:
        """
        Add a DNS record to a domain's zone.

        Args:
            domain: Domain name
            name: Record name (e.g., 'www', '@')
            record_type: Record type (A, AAAA, CNAME, TXT, MX)
            value: Record value
            ttl: Time to live in seconds (default: 14400)

        Returns:
            Dictionary with creation result.
        """
        async with CpanelClient() as client:
            # Use addzonerecord API
            params = {
                "domain": domain,
                "name": name if name != "@" else domain,
                "type": record_type,
                "ttl": ttl,
            }

            # Different fields for different record types
            if record_type in ("A", "AAAA"):
                params["address"] = value
            elif record_type == "CNAME":
                params["cname"] = value
            elif record_type == "TXT":
                params["txtdata"] = value
            elif record_type == "MX":
                # MX records need priority
                parts = value.split(" ", 1)
                if len(parts) == 2:
                    params["preference"] = parts[0]
                    params["exchange"] = parts[1]
                else:
                    params["preference"] = "10"
                    params["exchange"] = value

            result = await client.whm_api("addzonerecord", params=params)

            return {
                "domain": domain,
                "record_added": True,
                "name": name,
                "type": record_type,
                "value": value,
                "result": result.get("data", {}),
            }

    @mcp.tool()
    async def remove_dns_record(
        domain: str,
        line: int
    ) -> dict:
        """
        Remove a DNS record from a domain's zone.

        Args:
            domain: Domain name
            line: Line number of record to remove (from get_dns_zone)

        Returns:
            Dictionary with removal result.
        """
        async with CpanelClient() as client:
            result = await client.whm_api(
                "removezonerecord",
                params={"domain": domain, "line": line}
            )

            return {
                "domain": domain,
                "record_removed": True,
                "line": line,
                "result": result.get("data", {}),
            }

    @mcp.tool()
    async def list_ssl_certificates(username: Optional[str] = None) -> dict:
        """
        List SSL certificates on the server.

        Args:
            username: Optional - filter by cPanel username

        Returns:
            Dictionary with SSL certificate list.
        """
        async with CpanelClient() as client:
            params = {}
            if username:
                params["user"] = username

            result = await client.whm_api("listcrts", params=params)
            certs = result.get("data", {}).get("crt", [])

            formatted = []
            for cert in certs:
                formatted.append({
                    "domain": cert.get("subject.commonName"),
                    "issuer": cert.get("issuer.commonName"),
                    "not_before": cert.get("not_before"),
                    "not_after": cert.get("not_after"),
                    "user": cert.get("user"),
                })

            return {
                "certificates": formatted,
                "count": len(formatted),
            }

    @mcp.tool()
    async def check_domain_ssl(domain: str) -> dict:
        """
        Check SSL status for a domain.

        Args:
            domain: Domain name to check

        Returns:
            Dictionary with SSL certificate information including issuer and expiry.
        """
        async with CpanelClient() as client:
            try:
                # Use fetchsslinfo API which returns certificate data for a domain
                result = await client.whm_api(
                    "fetchsslinfo",
                    params={"domain": domain}
                )
                data = result.get("data", {})

                # If we got certificate data, SSL is installed
                crt_pem = data.get("crt")
                if crt_pem:
                    # Parse the certificate to get details
                    cert = x509.load_pem_x509_certificate(
                        crt_pem.encode(), default_backend()
                    )

                    # Extract issuer organization or CN
                    issuer_parts = []
                    for attr in cert.issuer:
                        if attr.oid == x509.oid.NameOID.ORGANIZATION_NAME:
                            issuer_parts.append(attr.value)
                        elif attr.oid == x509.oid.NameOID.COMMON_NAME:
                            issuer_parts.append(attr.value)

                    return {
                        "domain": domain,
                        "has_ssl": True,
                        "user": data.get("user"),
                        "ip": data.get("ip"),
                        "subject": cert.subject.get_attributes_for_oid(
                            x509.oid.NameOID.COMMON_NAME
                        )[0].value if cert.subject.get_attributes_for_oid(
                            x509.oid.NameOID.COMMON_NAME
                        ) else domain,
                        "issuer": ", ".join(issuer_parts) if issuer_parts else "Unknown",
                        "not_before": str(cert.not_valid_before_utc),
                        "not_after": str(cert.not_valid_after_utc),
                    }
                else:
                    return {
                        "domain": domain,
                        "has_ssl": False,
                    }
            except Exception as e:
                # If fetchsslinfo fails, domain may not have SSL
                logger.debug(f"SSL check for {domain}: {e}")
                return {
                    "domain": domain,
                    "has_ssl": False,
                    "error": str(e),
                }

    logger.info("Registered WHM domain tools")
