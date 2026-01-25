"""HTTP client for cPanel/WHM API."""

import logging
import ssl
from typing import Any, Optional

import aiohttp

from .config import CpanelConfig, get_config

logger = logging.getLogger(__name__)


class CpanelAPIError(Exception):
    """Exception for cPanel/WHM API errors."""

    def __init__(self, status: int, message: str, function: str):
        self.status = status
        self.message = message
        self.function = function
        super().__init__(f"cPanel API error {status} on {function}: {message}")


class CpanelClient:
    """Async HTTP client for cPanel/WHM API."""

    def __init__(self, config: Optional[CpanelConfig] = None):
        self.config = config or get_config()
        self._session: Optional[aiohttp.ClientSession] = None
        self._ssl_context: Optional[ssl.SSLContext] = None

        # Handle self-signed certs if allow_insecure
        if self.config.allow_insecure:
            self._ssl_context = ssl.create_default_context()
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE
            logger.warning("SSL verification disabled - use only in trusted environments")

    async def __aenter__(self) -> "CpanelClient":
        """Enter async context - create session."""
        timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)

        # WHM API token authentication header format
        # Authorization: whm {username}:{token}
        auth_header = f"whm {self.config.username}:{self.config.api_token.get_secret_value()}"

        connector = None
        if self._ssl_context:
            connector = aiohttp.TCPConnector(ssl=self._ssl_context)

        self._session = aiohttp.ClientSession(
            headers={
                "Authorization": auth_header,
                "Accept": "application/json",
            },
            timeout=timeout,
            connector=connector,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context - close session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def whm_api(
        self,
        function: str,
        params: Optional[dict] = None,
        api_version: int = 1,
    ) -> dict[str, Any]:
        """Call WHM API function.

        Args:
            function: WHM API function name (e.g., 'listaccts', 'accountsummary')
            params: Optional parameters for the function
            api_version: API version (default: 1)

        Returns:
            API response data
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use 'async with' context.")

        url = self.config.get_api_url(function, api_version)
        logger.debug(f"WHM API call: {function}")

        async with self._session.get(url, params=params) as resp:
            # Check HTTP status
            if resp.status >= 400:
                body = await resp.text()
                logger.error(f"WHM API error {resp.status}: {body}")
                raise CpanelAPIError(
                    status=resp.status,
                    message=body,
                    function=function,
                )

            data = await resp.json()

            # Check WHM API result
            # WHM API returns result: 1 for success, 0 for failure
            metadata = data.get("metadata", {})
            if metadata.get("result") == 0:
                reason = metadata.get("reason", "Unknown error")
                raise CpanelAPIError(
                    status=resp.status,
                    message=reason,
                    function=function,
                )

            return data

    async def cpanel_uapi(
        self,
        account: str,
        module: str,
        function: str,
        params: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Call cPanel UAPI for account-level operations.

        Args:
            account: cPanel account username
            module: UAPI module (e.g., 'Email', 'DomainInfo')
            function: UAPI function
            params: Optional parameters

        Returns:
            API response data
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use 'async with' context.")

        # Build URL with cpanel user parameter
        base_url = f"{self.config.whm_url}/execute/{module}/{function}"
        all_params = {"cpanel_jsonapi_user": account}
        if params:
            all_params.update(params)

        logger.debug(f"cPanel UAPI call: {account}:{module}:{function}")

        async with self._session.get(base_url, params=all_params) as resp:
            if resp.status >= 400:
                body = await resp.text()
                logger.error(f"cPanel UAPI error {resp.status}: {body}")
                raise CpanelAPIError(
                    status=resp.status,
                    message=body,
                    function=f"{module}/{function}",
                )

            data = await resp.json()

            # Check UAPI result
            if data.get("status") == 0:
                errors = data.get("errors", ["Unknown error"])
                raise CpanelAPIError(
                    status=resp.status,
                    message="; ".join(errors),
                    function=f"{module}/{function}",
                )

            return data


# Convenience function for getting a client instance
async def get_client() -> CpanelClient:
    """Get a configured client instance (use with async with)."""
    return CpanelClient()
