"""API client for Service.

This module provides a typed client for interacting with the Service API.
Customize the methods based on the actual API endpoints.
"""

import httpx
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class ServiceConfig:
    """Configuration for Service API client."""
    api_key: str
    base_url: str = "https://api.service.com"
    timeout: float = 30.0


class ServiceClient:
    """Client for Service API.

    Usage:
        client = ServiceClient(config)
        items = await client.list_items()
        item = await client.get_item("123")
    """

    def __init__(self, config: ServiceConfig):
        """Initialize the client.

        Args:
            config: Service configuration with API key and base URL
        """
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=config.timeout,
        )

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Make an API request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            json: JSON body data

        Returns:
            Response JSON data

        Raises:
            httpx.HTTPStatusError: On API error
        """
        response = await self.client.request(
            method,
            path,
            params=params,
            json=json,
        )
        response.raise_for_status()

        # Handle empty responses
        if response.status_code == 204:
            return {"success": True}

        return response.json()

    # -------------------------------------------------------------------------
    # List Operations
    # -------------------------------------------------------------------------

    async def list_items(
        self,
        limit: int = 50,
        offset: int = 0,
        filter_status: Optional[str] = None,
    ) -> dict[str, Any]:
        """List items with pagination.

        Args:
            limit: Maximum items to return
            offset: Number of items to skip
            filter_status: Optional status filter

        Returns:
            Dict with items list and pagination info
        """
        params = {"limit": limit, "offset": offset}
        if filter_status:
            params["status"] = filter_status

        return await self._request("GET", "/items", params=params)

    # -------------------------------------------------------------------------
    # Get Operations
    # -------------------------------------------------------------------------

    async def get_item(self, item_id: str) -> dict[str, Any]:
        """Get a specific item by ID.

        Args:
            item_id: The item identifier

        Returns:
            Item data
        """
        return await self._request("GET", f"/items/{item_id}")

    # -------------------------------------------------------------------------
    # Create Operations
    # -------------------------------------------------------------------------

    async def create_item(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new item.

        Args:
            data: Item data with required fields

        Returns:
            Created item with ID
        """
        return await self._request("POST", "/items", json=data)

    # -------------------------------------------------------------------------
    # Update Operations
    # -------------------------------------------------------------------------

    async def update_item(
        self,
        item_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an existing item.

        Args:
            item_id: The item identifier
            data: Fields to update

        Returns:
            Updated item data
        """
        return await self._request("PATCH", f"/items/{item_id}", json=data)

    # -------------------------------------------------------------------------
    # Delete Operations
    # -------------------------------------------------------------------------

    async def delete_item(self, item_id: str) -> dict[str, Any]:
        """Delete an item.

        Args:
            item_id: The item identifier

        Returns:
            Success confirmation
        """
        return await self._request("DELETE", f"/items/{item_id}")

    # -------------------------------------------------------------------------
    # Search Operations
    # -------------------------------------------------------------------------

    async def search_items(
        self,
        query: str,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Search items by query string.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Search results with items
        """
        return await self._request(
            "GET",
            "/items/search",
            params={"q": query, "limit": limit},
        )

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    async def close(self):
        """Close the HTTP client connection."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
