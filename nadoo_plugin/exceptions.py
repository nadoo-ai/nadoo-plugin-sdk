"""
Nadoo Plugin SDK Exceptions
"""


class NadooPluginError(Exception):
    """Base exception for all Nadoo Plugin errors"""

    pass


class PluginConfigurationError(NadooPluginError):
    """Raised when plugin configuration is invalid"""

    pass


class PluginExecutionError(NadooPluginError):
    """Raised when plugin execution fails"""

    pass


class PluginPermissionError(NadooPluginError):
    """Raised when plugin lacks required permission"""

    pass


class PluginValidationError(NadooPluginError):
    """Raised when plugin validation fails"""

    pass


class PluginTimeoutError(NadooPluginError):
    """Raised when plugin execution times out"""

    pass


class PluginResourceLimitError(NadooPluginError):
    """Raised when plugin exceeds resource limits"""

    pass


class InternalAPIError(NadooPluginError):
    """Raised when Internal API call fails"""

    pass


class LLMInvocationError(InternalAPIError):
    """Raised when LLM invocation fails"""

    pass


class ToolInvocationError(InternalAPIError):
    """Raised when tool invocation fails"""

    pass


class KnowledgeSearchError(InternalAPIError):
    """Raised when knowledge search fails"""

    pass


class StorageError(InternalAPIError):
    """Raised when storage operation fails"""

    pass
