"""
Base plugin class
"""

import inspect
from typing import Any, Dict, List, Optional

from .context import PluginContext
from .api.client import InternalAPIClient
from .exceptions import PluginConfigurationError, PluginExecutionError


class NadooPlugin:
    """
    Base class for all Nadoo plugins

    All plugins must inherit from this class and implement their tools as methods
    decorated with @tool.

    Example:
        class MyPlugin(NadooPlugin):
            def on_initialize(self):
                self.api_key = self.require_env("API_KEY")

            @tool(name="my_tool", description="Does something")
            @parameter("input", type="string", required=True)
            def my_tool(self, input: str) -> dict:
                return {"result": input.upper()}
    """

    def __init__(self):
        self.context: Optional[PluginContext] = None
        self.api: Optional[InternalAPIClient] = None
        self._tools: Dict[str, callable] = {}
        self._initialized = False

    def initialize(self, context: PluginContext, api: InternalAPIClient):
        """
        Initialize plugin with context and API client

        This is called by the plugin executor before any tool execution.
        DO NOT override this method - use on_initialize() instead.
        """
        if context is None:
            raise PluginConfigurationError("Context cannot be None")
        if api is None:
            raise PluginConfigurationError("API client cannot be None")

        self.context = context
        self.api = api

        # Discover tools
        self._discover_tools()

        # Call user initialization
        try:
            self.on_initialize()
            self._initialized = True
            self.context.info(f"Plugin initialized: {self.__class__.__name__}")
        except Exception as e:
            self.context.error(f"Plugin initialization failed: {str(e)}")
            raise PluginConfigurationError(f"Failed to initialize plugin: {str(e)}") from e

    def finalize(self):
        """
        Finalize plugin

        This is called by the plugin executor after tool execution.
        DO NOT override this method - use on_finalize() instead.
        """
        try:
            self.on_finalize()
            self.context.info(f"Plugin finalized: {self.__class__.__name__}")
        except Exception as e:
            self.context.warn(f"Plugin finalization error: {str(e)}")

        # Close API clients
        if self.api:
            self.api.close()

    def on_initialize(self):
        """
        Override this method to perform plugin initialization

        Example:
            def on_initialize(self):
                self.api_key = self.require_env("API_KEY")
                self.endpoint = self.get_env("API_ENDPOINT", "https://api.example.com")
                self.context.log("Initialization complete")
        """
        pass

    def on_finalize(self):
        """
        Override this method to perform cleanup before shutdown

        Example:
            def on_finalize(self):
                self.context.log("Cleaning up...")
                # Close connections, save state, etc.
        """
        pass

    def _discover_tools(self):
        """Discover all methods decorated with @tool"""
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, "_is_tool") and hasattr(method, "_tool_metadata"):
                metadata = method._tool_metadata
                self._tools[metadata.name] = method
                self.context.debug(f"Discovered tool: {metadata.name}")

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool

        This is called by the plugin executor.
        DO NOT call this method directly.
        """
        if not self._initialized:
            raise PluginExecutionError("Plugin not initialized")

        # Find tool
        if tool_name not in self._tools:
            available_tools = ", ".join(self._tools.keys())
            raise PluginExecutionError(
                f"Tool '{tool_name}' not found. Available tools: {available_tools}"
            )

        tool_method = self._tools[tool_name]
        metadata = tool_method._tool_metadata

        # Log execution
        self.context.info(f"Executing tool: {tool_name}")
        self.context.start_step(f"tool:{tool_name}")

        try:
            # Fill in default values for missing parameters
            final_parameters = (parameters or {}).copy()
            for param_def in metadata.parameters:
                param_name = param_def["name"]
                if param_name not in final_parameters and "default" in param_def:
                    final_parameters[param_name] = param_def["default"]

            # Execute tool
            result = tool_method(**final_parameters)

            # Validate result
            if not isinstance(result, dict):
                raise PluginExecutionError(
                    f"Tool must return a dict, got {type(result).__name__}"
                )

            self.context.end_step()
            self.context.info(f"Tool executed successfully: {tool_name}")

            return result

        except Exception as e:
            self.context.end_step()
            self.context.error(f"Tool execution failed: {str(e)}")
            raise PluginExecutionError(f"Tool '{tool_name}' failed: {str(e)}") from e

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with metadata"""
        tools = []
        for tool_name, method in self._tools.items():
            metadata = method._tool_metadata
            tools.append(
                {
                    "name": metadata.name,
                    "description": metadata.description,
                    "parameters": metadata.parameters,
                    "required_permissions": metadata.required_permissions,
                }
            )
        return tools

    # ==================== Convenience Methods ====================

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable

        Example:
            endpoint = self.get_env("API_ENDPOINT", "https://default.com")
        """
        return self.context.get_env(key, default)

    def require_env(self, key: str) -> str:
        """
        Require environment variable (raises error if not set)

        Example:
            api_key = self.require_env("API_KEY")
        """
        return self.context.require_env(key)

    def log(self, message: str, level: str = "info"):
        """
        Log a message

        Example:
            self.log("Processing started")
            self.log("Something went wrong", level="error")
        """
        self.context.log(message, level)

    def watch(self, name: str, value: Any):
        """
        Watch a variable for debugging

        Example:
            self.watch("input_length", len(input))
            self.watch("api_response", response)
        """
        self.context.watch_variable(name, value)
