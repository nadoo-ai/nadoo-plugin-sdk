"""
Decorators for plugin development
"""

import functools
from typing import Any, Callable, Dict, List, Literal, Optional


class ToolMetadata:
    """Metadata for a plugin tool"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.parameters: List[Dict[str, Any]] = []
        self.required_permissions: List[str] = []


class ParameterMetadata:
    """Metadata for a tool parameter"""

    def __init__(
        self,
        name: str,
        type: Literal["string", "number", "boolean", "array", "object"],
        required: bool = True,
        default: Any = None,
        description: Optional[str] = None,
    ):
        self.name = name
        self.type = type
        self.required = required
        self.default = default
        self.description = description

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "type": self.type,
            "required": self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        if self.description:
            result["description"] = self.description
        return result


def tool(name: str, description: str) -> Callable:
    """
    Decorator to mark a method as a plugin tool

    Usage:
        @tool(name="my_tool", description="Does something useful")
        def my_tool(self, param1: str) -> dict:
            return {"result": param1}
    """

    def decorator(func: Callable) -> Callable:
        # Create metadata
        metadata = ToolMetadata(name=name, description=description)

        # Attach metadata to function
        if not hasattr(func, "_tool_metadata"):
            func._tool_metadata = metadata
        else:
            func._tool_metadata.name = name
            func._tool_metadata.description = description

        # Mark as tool
        func._is_tool = True

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Copy metadata to wrapper
        wrapper._tool_metadata = metadata
        wrapper._is_tool = True

        return wrapper

    return decorator


def parameter(
    name: str,
    type: Literal["string", "number", "boolean", "array", "object"] = "string",
    required: bool = True,
    default: Any = None,
    description: Optional[str] = None,
) -> Callable:
    """
    Decorator to define a tool parameter

    Usage:
        @tool(name="my_tool", description="Does something")
        @parameter("input", type="string", required=True, description="Input text")
        @parameter("mode", type="string", default="standard", description="Processing mode")
        def my_tool(self, input: str, mode: str = "standard") -> dict:
            return {"result": input, "mode": mode}
    """

    def decorator(func: Callable) -> Callable:
        # Ensure tool metadata exists
        if not hasattr(func, "_tool_metadata"):
            func._tool_metadata = ToolMetadata(name="", description="")

        # Add parameter metadata
        param_metadata = ParameterMetadata(
            name=name, type=type, required=required, default=default, description=description
        )

        # Insert at beginning (decorators are applied bottom-up)
        func._tool_metadata.parameters.insert(0, param_metadata.to_dict())

        return func

    return decorator


def permission_required(*permissions: str) -> Callable:
    """
    Decorator to require specific permissions

    Usage:
        @tool(name="my_tool", description="Uses LLM")
        @permission_required("llm_access", "storage")
        def my_tool(self, input: str) -> dict:
            # Will check for permissions before execution
            return {}
    """

    def decorator(func: Callable) -> Callable:
        # Ensure tool metadata exists
        if not hasattr(func, "_tool_metadata"):
            func._tool_metadata = ToolMetadata(name="", description="")

        # Add required permissions
        func._tool_metadata.required_permissions.extend(permissions)

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Check permissions at runtime
            for permission in permissions:
                self.context.require_permission(permission)

            # Execute original function
            return func(self, *args, **kwargs)

        # Copy metadata
        wrapper._tool_metadata = func._tool_metadata
        if hasattr(func, "_is_tool"):
            wrapper._is_tool = func._is_tool

        return wrapper

    return decorator


def validator(
    param_name: str,
    allowed_values: Optional[List[Any]] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
) -> Callable:
    """
    Decorator to validate parameter values

    Usage:
        @tool(name="format_text", description="Format text")
        @parameter("format", type="string", required=True)
        @validator("format", allowed_values=["upper", "lower", "title", "capitalize"])
        def format_text(self, text: str, format: str) -> dict:
            # format will be validated before this runs
            return {"formatted": text.upper() if format == "upper" else text}
    """
    import re

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get parameter value
            param_value = kwargs.get(param_name)

            # Skip validation if parameter was not provided (will use default)
            if param_value is None:
                return func(self, *args, **kwargs)

            # Validate allowed values
            if allowed_values is not None:
                if param_value not in allowed_values:
                    raise ValueError(
                        f"Parameter '{param_name}' must be one of {allowed_values}, got: {param_value}"
                    )

            # Validate numeric range
            if isinstance(param_value, (int, float)):
                if min_value is not None and param_value < min_value:
                    raise ValueError(f"Parameter '{param_name}' must be >= {min_value}, got: {param_value}")
                if max_value is not None and param_value > max_value:
                    raise ValueError(f"Parameter '{param_name}' must be <= {max_value}, got: {param_value}")

            # Validate string length
            if isinstance(param_value, str):
                if min_length is not None and len(param_value) < min_length:
                    raise ValueError(
                        f"Parameter '{param_name}' must have length >= {min_length}, got: {len(param_value)}"
                    )
                if max_length is not None and len(param_value) > max_length:
                    raise ValueError(
                        f"Parameter '{param_name}' must have length <= {max_length}, got: {len(param_value)}"
                    )

                # Validate pattern
                if pattern is not None:
                    if not re.match(pattern, param_value):
                        raise ValueError(f"Parameter '{param_name}' does not match pattern: {pattern}")

            # Execute original function
            return func(self, *args, **kwargs)

        # Copy metadata
        if hasattr(func, "_tool_metadata"):
            wrapper._tool_metadata = func._tool_metadata
        if hasattr(func, "_is_tool"):
            wrapper._is_tool = func._is_tool

        return wrapper

    return decorator


def validate_parameters(schema: Dict[str, Any]) -> Callable:
    """
    Decorator to validate parameters against schema (advanced)

    Usage:
        @tool(name="my_tool", description="Validates input")
        @validate_parameters({
            "email": {"type": "string", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
            "age": {"type": "number", "min": 0, "max": 150}
        })
        def my_tool(self, email: str, age: int) -> dict:
            return {"valid": True}
    """
    import re

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Validate each parameter in schema
            for param_name, constraints in schema.items():
                value = kwargs.get(param_name)

                if value is None:
                    continue

                # Type validation
                param_type = constraints.get("type")
                if param_type == "string" and not isinstance(value, str):
                    raise TypeError(f"Parameter '{param_name}' must be a string")
                elif param_type == "number" and not isinstance(value, (int, float)):
                    raise TypeError(f"Parameter '{param_name}' must be a number")
                elif param_type == "boolean" and not isinstance(value, bool):
                    raise TypeError(f"Parameter '{param_name}' must be a boolean")
                elif param_type == "array" and not isinstance(value, list):
                    raise TypeError(f"Parameter '{param_name}' must be an array")
                elif param_type == "object" and not isinstance(value, dict):
                    raise TypeError(f"Parameter '{param_name}' must be an object")

                # Numeric constraints
                if "min" in constraints and value < constraints["min"]:
                    raise ValueError(f"Parameter '{param_name}' must be >= {constraints['min']}")
                if "max" in constraints and value > constraints["max"]:
                    raise ValueError(f"Parameter '{param_name}' must be <= {constraints['max']}")

                # String constraints
                if "min_length" in constraints and len(value) < constraints["min_length"]:
                    raise ValueError(f"Parameter '{param_name}' length must be >= {constraints['min_length']}")
                if "max_length" in constraints and len(value) > constraints["max_length"]:
                    raise ValueError(f"Parameter '{param_name}' length must be <= {constraints['max_length']}")

                # Pattern validation
                if "pattern" in constraints:
                    if not re.match(constraints["pattern"], value):
                        raise ValueError(f"Parameter '{param_name}' does not match pattern")

            return func(self, *args, **kwargs)

        # Copy metadata
        if hasattr(func, "_tool_metadata"):
            wrapper._tool_metadata = func._tool_metadata
        if hasattr(func, "_is_tool"):
            wrapper._is_tool = func._is_tool

        return wrapper

    return decorator


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable:
    """
    Decorator to retry failed executions

    Usage:
        @tool(name="my_tool", description="May fail")
        @retry(max_attempts=3, delay=1.0, backoff=2.0)
        def my_tool(self, url: str) -> dict:
            # Will retry up to 3 times with exponential backoff
            response = requests.get(url)
            return response.json()
    """
    import time

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay

            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise

                    # Log retry attempt
                    if len(args) > 0 and hasattr(args[0], "context"):
                        args[0].context.warn(
                            f"Retry attempt {attempt}/{max_attempts} after error: {str(e)}"
                        )

                    time.sleep(current_delay)
                    current_delay *= backoff

        # Copy metadata
        if hasattr(func, "_tool_metadata"):
            wrapper._tool_metadata = func._tool_metadata
        if hasattr(func, "_is_tool"):
            wrapper._is_tool = func._is_tool

        return wrapper

    return decorator
