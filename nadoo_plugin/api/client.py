"""
Base Internal API client
"""

import httpx
import time
from typing import Any, Dict, Optional

from ..context import PluginContext
from ..exceptions import InternalAPIError


class BaseAPIClient:
    """Base HTTP client for Internal API"""

    def __init__(self, base_url: str, token: str, context: Optional[PluginContext] = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.context = context
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def _get_headers(self) -> Dict[str, str]:
        """Get common headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "nadoo-plugin-sdk/0.1.0",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        api_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with automatic tracking"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Start timing
        start_time = time.time()
        error_msg = None
        result = None

        try:
            response = self._client.request(
                method=method, url=url, json=json, params=params, headers=self._get_headers()
            )

            response.raise_for_status()
            result = response.json()

            return result

        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except:
                error_detail = str(e)

            error_msg = f"API request failed: {error_detail}"
            raise InternalAPIError(error_msg) from e

        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            raise InternalAPIError(error_msg) from e

        finally:
            # Record API call if context available
            duration = time.time() - start_time
            if self.context and api_type:
                self.context.record_api_call(
                    api_type=api_type,
                    endpoint=endpoint,
                    parameters=json or params or {},
                    result=result,
                    duration=duration,
                    error=error_msg,
                )

    def close(self):
        """Close HTTP client"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class InternalAPIClient:
    """
    Main Internal API client

    Provides access to all Nadoo services from plugins.
    """

    def __init__(self, base_url: str, token: str, context: PluginContext):
        from .llm import LLMClient
        from .tools import ToolsClient
        from .knowledge import KnowledgeClient
        from .storage import StorageClient

        self.base_url = base_url
        self.token = token
        self.context = context

        # Initialize sub-clients
        self.llm = LLMClient(base_url, token, context)
        self.tools = ToolsClient(base_url, token, context)
        self.knowledge = KnowledgeClient(base_url, token, context)
        self.storage = StorageClient(base_url, token, context)

    def close(self):
        """Close all clients"""
        self.llm.close()
        self.tools.close()
        self.knowledge.close()
        self.storage.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
