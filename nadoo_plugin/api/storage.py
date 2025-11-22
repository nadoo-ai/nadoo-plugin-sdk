"""
Storage API client
"""

from typing import Any, Optional

from ..context import PluginContext
from ..exceptions import StorageError
from .client import BaseAPIClient


class StorageClient(BaseAPIClient):
    """
    Storage API client

    Allows plugins to store persistent data (scoped to plugin).
    """

    def __init__(self, base_url: str, token: str, context: PluginContext):
        super().__init__(base_url, token, context)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value

        Args:
            key: Storage key (scoped to plugin)
            value: Value to store (must be JSON-serializable)
            ttl: Time-to-live in seconds (optional)

        Returns:
            True if successful

        Raises:
            PluginPermissionError: If 'storage' permission not granted
            StorageError: If operation fails

        Example:
            # Store data
            self.api.storage.set("user_count", 42)

            # Store with TTL (expires after 1 hour)
            self.api.storage.set("temp_data", {"value": 123}, ttl=3600)
        """
        # Check permission
        self.context.require_permission("storage")

        # Validate key
        if not key or len(key) > 255:
            raise ValueError("Key must be 1-255 characters")

        # Log API call
        self.context.debug(f"Storage set: {key}")

        # Prepare request
        payload = {"key": key, "value": value}
        if ttl:
            payload["ttl"] = ttl

        try:
            # Make API call (with automatic tracking)
            self._request("POST", "/internal-api/plugin/invoke/storage/set", json=payload, api_type="storage")

            # Log result
            self.context.info(f"Storage set: {key}")

            return True

        except Exception as e:
            self.context.error(f"Storage set failed: {str(e)}")
            raise StorageError(f"Failed to store value: {str(e)}") from e

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value

        Args:
            key: Storage key
            default: Default value if key doesn't exist

        Returns:
            Stored value or default

        Raises:
            PluginPermissionError: If 'storage' permission not granted
            StorageError: If operation fails

        Example:
            # Get value
            count = self.api.storage.get("user_count", default=0)
            print(f"User count: {count}")
        """
        # Check permission
        self.context.require_permission("storage")

        # Log API call
        self.context.debug(f"Storage get: {key}")

        try:
            # Make API call (with automatic tracking)
            response = self._request("GET", f"/internal-api/plugin/invoke/storage/get/{key}", api_type="storage")

            # Log result
            self.context.info(f"Storage get: {key}")

            return response.get("value", default)

        except Exception as e:
            # If key not found, return default
            if "404" in str(e) or "not found" in str(e).lower():
                self.context.debug(f"Storage key not found: {key}, returning default")
                return default

            self.context.error(f"Storage get failed: {str(e)}")
            raise StorageError(f"Failed to retrieve value: {str(e)}") from e

    def delete(self, key: str) -> bool:
        """
        Delete a value

        Args:
            key: Storage key

        Returns:
            True if successful

        Raises:
            PluginPermissionError: If 'storage' permission not granted
            StorageError: If operation fails

        Example:
            # Delete value
            self.api.storage.delete("temp_data")
        """
        # Check permission
        self.context.require_permission("storage")

        # Log API call
        self.context.debug(f"Storage delete: {key}")

        try:
            # Make API call (with automatic tracking)
            self._request("DELETE", f"/internal-api/plugin/invoke/storage/delete/{key}", api_type="storage")

            # Log result
            self.context.info(f"Storage delete: {key}")

            return True

        except Exception as e:
            self.context.error(f"Storage delete failed: {str(e)}")
            raise StorageError(f"Failed to delete value: {str(e)}") from e

    def list_keys(self, prefix: Optional[str] = None) -> list:
        """
        List all keys (optionally filtered by prefix)

        Args:
            prefix: Key prefix filter (optional)

        Returns:
            List of keys

        Raises:
            PluginPermissionError: If 'storage' permission not granted
            StorageError: If operation fails

        Example:
            # List all keys
            keys = self.api.storage.list_keys()
            print(f"Total keys: {len(keys)}")

            # List keys with prefix
            user_keys = self.api.storage.list_keys(prefix="user:")
        """
        # Check permission
        self.context.require_permission("storage")

        # Log API call
        self.context.debug(f"Storage list keys: prefix={prefix}")

        try:
            # Prepare params
            params = {}
            if prefix:
                params["prefix"] = prefix

            # Make API call (with automatic tracking)
            response = self._request("GET", "/internal-api/plugin/invoke/storage/keys", params=params, api_type="storage")

            # Log result
            keys = response.get("keys", [])
            self.context.info(f"Storage list keys: {len(keys)} keys")

            return keys

        except Exception as e:
            self.context.error(f"Storage list keys failed: {str(e)}")
            raise StorageError(f"Failed to list keys: {str(e)}") from e
