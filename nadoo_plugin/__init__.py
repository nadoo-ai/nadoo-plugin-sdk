"""
Nadoo Plugin SDK

Official Python SDK for developing plugins for Nadoo AI Platform.

Example:
    from nadoo_plugin import NadooPlugin, tool, parameter

    class MyPlugin(NadooPlugin):
        @tool(name="my_tool", description="Does something useful")
        @parameter("input", type="string", required=True)
        def my_tool(self, input: str) -> dict:
            return {"result": input.upper()}
"""

__version__ = "0.1.0"
__author__ = "Nadoo Team"
__license__ = "MIT"

# Core classes
from .plugin import NadooPlugin
from .context import PluginContext

# Decorators
from .decorators import (
    tool,
    parameter,
    permission_required,
    validator,
    validate_parameters,
    retry,
)

# Exceptions
from .exceptions import (
    NadooPluginError,
    PluginConfigurationError,
    PluginExecutionError,
    PluginPermissionError,
    PluginValidationError,
    PluginTimeoutError,
    PluginResourceLimitError,
    InternalAPIError,
    LLMInvocationError,
    ToolInvocationError,
    KnowledgeSearchError,
    StorageError,
)

# API clients
from .api import (
    InternalAPIClient,
    LLMClient,
    LLMResponse,
    ToolsClient,
    KnowledgeClient,
    KnowledgeSearchResult,
    StorageClient,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "NadooPlugin",
    "PluginContext",
    # Decorators
    "tool",
    "parameter",
    "permission_required",
    "validator",
    "validate_parameters",
    "retry",
    # Exceptions
    "NadooPluginError",
    "PluginConfigurationError",
    "PluginExecutionError",
    "PluginPermissionError",
    "PluginValidationError",
    "PluginTimeoutError",
    "PluginResourceLimitError",
    "InternalAPIError",
    "LLMInvocationError",
    "ToolInvocationError",
    "KnowledgeSearchError",
    "StorageError",
    # API
    "InternalAPIClient",
    "LLMClient",
    "LLMResponse",
    "ToolsClient",
    "KnowledgeClient",
    "KnowledgeSearchResult",
    "StorageClient",
]
