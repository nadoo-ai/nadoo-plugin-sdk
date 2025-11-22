"""
Tools API client
"""

from typing import Any, Dict, Optional

from ..context import PluginContext
from ..exceptions import ToolInvocationError
from .client import BaseAPIClient


class ToolsClient(BaseAPIClient):
    """
    Tools API client

    Allows plugins to invoke other tools.
    """

    def __init__(self, base_url: str, token: str, context: PluginContext):
        super().__init__(base_url, token, context)

    def invoke(
        self,
        tool_uuid: Optional[str] = None,
        tool_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke a tool

        Args:
            tool_uuid: Tool UUID (for custom tools)
            tool_name: Tool name (for built-in tools)
            parameters: Tool parameters

        Returns:
            Tool execution result

        Raises:
            PluginPermissionError: If 'tool_invocation' permission not granted
            ToolInvocationError: If invocation fails

        Example:
            # Invoke built-in tool
            result = self.api.tools.invoke(
                tool_name="web_search",
                parameters={"query": "AI news"}
            )

            # Invoke custom tool by UUID
            result = self.api.tools.invoke(
                tool_uuid="tool-uuid-123",
                parameters={"input": "data"}
            )
        """
        # Check permission
        self.context.require_permission("tool_invocation")

        # Validate input
        if not tool_uuid and not tool_name:
            raise ValueError("Either tool_uuid or tool_name must be provided")

        # Log API call
        identifier = tool_uuid or tool_name
        self.context.debug(f"Tool invoke: {identifier}")

        # Prepare request
        payload = {"parameters": parameters or {}}

        if tool_uuid:
            payload["tool_uuid"] = tool_uuid
        if tool_name:
            payload["tool_name"] = tool_name

        try:
            # Make API call (with automatic tracking)
            response = self._request("POST", "/internal-api/plugin/invoke/tool", json=payload, api_type="tool")

            # Log result
            self.context.info(f"Tool invoked: {identifier}")

            return response

        except Exception as e:
            self.context.error(f"Tool invocation failed: {str(e)}")
            raise ToolInvocationError(f"Failed to invoke tool: {str(e)}") from e
