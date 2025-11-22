"""
Plugin execution context
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


class LogEntry:
    """Log entry"""

    def __init__(self, level: str, message: str, timestamp: datetime = None):
        self.level = level
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> dict:
        return {"level": self.level, "message": self.message, "timestamp": self.timestamp.isoformat()}


class TraceEntry:
    """Trace entry for execution events"""

    def __init__(
        self,
        event: str,
        data: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        step: Optional[str] = None,
        execution_time: float = 0.0,
    ):
        self.timestamp = datetime.utcnow()
        self.event = event
        self.data = data
        self.metadata = metadata or {}
        self.step = step
        self.execution_time = execution_time

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event": self.event,
            "data": self._serialize_value(self.data),
            "metadata": self.metadata,
            "step": self.step,
            "execution_time": self.execution_time,
        }

    def _serialize_value(self, value: Any) -> Any:
        """Serialize value for JSON"""
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value[:10]]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in list(value.items())[:10]}
        else:
            return {"_type": type(value).__name__, "_repr": repr(value)[:200]}


class StepEntry:
    """Step entry for step timing"""

    def __init__(self, step_name: str, started_at: datetime = None):
        self.step_name = step_name
        self.started_at = started_at or datetime.utcnow()
        self.ended_at: Optional[datetime] = None
        self.duration: Optional[float] = None

    def end(self):
        """End the step"""
        self.ended_at = datetime.utcnow()
        self.duration = (self.ended_at - self.started_at).total_seconds()

    def to_dict(self) -> dict:
        return {
            "step_name": self.step_name,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration": self.duration,
        }


class VariableSnapshot:
    """Variable snapshot for debugging"""

    def __init__(self, name: str, value: Any, metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.value = value
        self.value_type = type(value).__name__
        self.timestamp = datetime.utcnow()
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self._serialize_value(self.value),
            "value_type": self.value_type,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    def _serialize_value(self, value: Any) -> Any:
        """Serialize value for JSON"""
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value[:10]]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in list(value.items())[:10]}
        else:
            return {"_type": type(value).__name__, "_repr": repr(value)[:200]}


class APICallRecord:
    """API call record for debugging"""

    def __init__(
        self,
        api_type: str,
        endpoint: str,
        parameters: Dict[str, Any],
        result: Any = None,
        duration: float = 0.0,
        error: Optional[str] = None,
    ):
        self.timestamp = datetime.utcnow()
        self.api_type = api_type
        self.endpoint = endpoint
        self.parameters = parameters
        self.result = result
        self.duration = duration
        self.error = error
        self.success = error is None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "api_type": self.api_type,
            "endpoint": self.endpoint,
            "parameters": self._sanitize_parameters(self.parameters),
            "result": self._serialize_value(self.result),
            "duration": self.duration,
            "error": self.error,
            "success": self.success,
        }

    def _sanitize_parameters(self, params: Dict) -> Dict:
        """Remove sensitive data from parameters"""
        sanitized = params.copy()
        sensitive_keys = ["api_key", "password", "token", "secret", "authorization"]

        for key in list(sanitized.keys()):
            if any(s in key.lower() for s in sensitive_keys):
                sanitized[key] = "***REDACTED***"

        return sanitized

    def _serialize_value(self, value: Any) -> Any:
        """Serialize value for JSON"""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value[:10]]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in list(value.items())[:10]}
        else:
            return {"_type": type(value).__name__, "_repr": repr(value)[:200]}


class PluginContext:
    """
    Plugin execution context

    Provides logging, tracing, and variable watching capabilities.
    """

    def __init__(
        self,
        execution_id: str,
        plugin_id: str,
        workspace_id: str,
        user_id: Optional[str] = None,
        application_id: Optional[str] = None,
        model_uuid: Optional[str] = None,
        workflow_id: Optional[str] = None,
        node_id: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        allowed_tool_ids: Optional[List[str]] = None,
        allowed_kb_ids: Optional[List[str]] = None,
        sdk_version: Optional[str] = None,
        plugin_version: Optional[str] = None,
        debug_mode: bool = False,
    ):
        # Identity
        self.execution_id = execution_id
        self.plugin_id = plugin_id
        self.workspace_id = workspace_id
        self.user_id = user_id

        # Application context
        self.application_id = application_id
        self.model_uuid = model_uuid

        # Workflow context
        self.workflow_id = workflow_id
        self.node_id = node_id

        # Version info
        self.sdk_version = sdk_version  # Current SDK version
        self.plugin_version = plugin_version  # Plugin's version

        # Permissions
        self.permissions = set(permissions or [])
        self.allowed_tool_ids = allowed_tool_ids or []
        self.allowed_kb_ids = allowed_kb_ids or []

        # Debug mode
        self.debug_mode = debug_mode

        # Internal state
        self._logs: List[LogEntry] = []
        self._trace: List[TraceEntry] = []
        self._steps: List[StepEntry] = []
        self._variables: Dict[str, VariableSnapshot] = {}
        self._api_calls: List[APICallRecord] = []
        self._current_step: Optional[StepEntry] = None
        self._current_step_name: Optional[str] = None
        self._started_at = datetime.utcnow()

    # ==================== Logging ====================

    def log(self, message: str, level: str = "info"):
        """Log a message"""
        entry = LogEntry(level=level, message=message)
        self._logs.append(entry)
        if self.debug_mode:
            print(f"[{level.upper()}] {message}")

    def info(self, message: str):
        """Log info message"""
        self.log(message, "info")

    def warn(self, message: str):
        """Log warning message"""
        self.log(message, "warn")

    def error(self, message: str):
        """Log error message"""
        self.log(message, "error")

    def debug(self, message: str):
        """Log debug message (only in debug mode)"""
        if self.debug_mode:
            self.log(message, "debug")

    # ==================== Tracing ====================

    def trace(self, event: str, data: Any = None, **metadata):
        """
        Record execution trace event.

        Args:
            event: Event name (e.g., "data_loaded", "api_called")
            data: Event data
            **metadata: Additional metadata

        Example:
            self.context.trace("data_loaded", {
                "rows": len(df),
                "columns": df.columns.tolist()
            }, source="database")
        """
        entry = TraceEntry(
            event=event,
            data=data,
            metadata=metadata,
            step=self._current_step_name,
            execution_time=self.get_execution_time(),
        )
        self._trace.append(entry)
        self.debug(f"Trace event: {event}")

    def add_trace(self, event: str, data: Any = None, **metadata):
        """
        Alias for trace() method for backwards compatibility.

        Args:
            event: Event name (e.g., "custom_event", "milestone_reached")
            data: Event data
            **metadata: Additional metadata

        Example:
            self.context.add_trace("custom_event", data={"status": "success"})
        """
        self.trace(event, data, **metadata)

    def start_step(self, step_name: str):
        """
        Start timing a step.

        Example:
            self.context.start_step("data_processing")
            # ... processing code ...
            self.context.end_step()
        """
        # Auto-end previous step
        if self._current_step:
            self.end_step()

        self._current_step = StepEntry(step_name)
        self._current_step_name = step_name
        self._steps.append(self._current_step)
        self.trace("step_started", {"step": step_name})
        self.debug(f"Started step: {step_name}")

    def end_step(self):
        """End current step and record timing"""
        if self._current_step:
            self._current_step.end()
            self.trace(
                "step_completed",
                {"step": self._current_step.step_name, "duration_seconds": self._current_step.duration},
            )
            self.debug(f"Ended step: {self._current_step.step_name} ({self._current_step.duration:.3f}s)")
            self._current_step = None
            self._current_step_name = None

    # ==================== Variables ====================

    def watch_variable(self, name: str, value: Any, **metadata):
        """
        Watch variable value (captures snapshot).

        Args:
            name: Variable name
            value: Variable value
            **metadata: Additional metadata

        Example:
            results = process_data(data)
            self.context.watch_variable("results", results, type="list", count=len(results))
        """
        snapshot = VariableSnapshot(name=name, value=value, metadata=metadata)
        self._variables[name] = snapshot

        # Trace variable change
        self.trace("variable_changed", {"variable": name, "type": snapshot.value_type})
        self.debug(f"Variable: {name} = {value}")

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get watched variable value"""
        snapshot = self._variables.get(name)
        return snapshot.value if snapshot else default

    # ==================== API Call Tracking ====================

    def record_api_call(
        self,
        api_type: str,
        endpoint: str,
        parameters: Dict[str, Any],
        result: Any = None,
        duration: float = 0.0,
        error: Optional[str] = None,
    ):
        """
        Record API call (automatically called by Internal API client).

        Args:
            api_type: Type of API (llm, tool, knowledge, storage, etc.)
            endpoint: API endpoint
            parameters: Request parameters
            result: API result
            duration: Execution duration (seconds)
            error: Error message if failed
        """
        record = APICallRecord(
            api_type=api_type,
            endpoint=endpoint,
            parameters=parameters,
            result=result,
            duration=duration,
            error=error,
        )
        self._api_calls.append(record)

        self.trace("api_called", {"api_type": api_type, "success": record.success, "duration": duration})
        self.debug(f"API call: {api_type} {endpoint} - {'success' if record.success else 'failed'}")

    # ==================== Permissions ====================

    def has_permission(self, permission: str) -> bool:
        """Check if plugin has permission"""
        return permission in self.permissions

    def require_permission(self, permission: str):
        """Require a permission (raises error if not granted)"""
        if not self.has_permission(permission):
            from .exceptions import PluginPermissionError

            raise PluginPermissionError(f"Plugin requires '{permission}' permission")

    # ==================== Environment Variables ====================

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable"""
        return os.environ.get(key, default)

    def require_env(self, key: str) -> str:
        """Require environment variable (raises error if not set)"""
        value = os.environ.get(key)
        if value is None:
            from .exceptions import PluginConfigurationError

            raise PluginConfigurationError(f"Required environment variable '{key}' is not set")
        return value

    # ==================== Debug Info ====================

    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all log entries"""
        return [entry.to_dict() for entry in self._logs]

    def get_trace(self) -> List[Dict[str, Any]]:
        """Get all trace entries"""
        return [entry.to_dict() for entry in self._trace]

    def get_steps(self) -> List[Dict[str, Any]]:
        """Get all step entries"""
        return [step.to_dict() for step in self._steps]

    def get_variables(self) -> Dict[str, Any]:
        """Get all watched variables"""
        return {name: snapshot.to_dict() for name, snapshot in self._variables.items()}

    def get_api_calls(self) -> List[Dict[str, Any]]:
        """Get all API call records"""
        return [call.to_dict() for call in self._api_calls]

    def get_step_timings(self) -> Dict[str, float]:
        """Get step timings"""
        return {step.step_name: step.duration for step in self._steps if step.duration is not None}

    def get_execution_time(self) -> float:
        """Get total execution time in seconds"""
        return (datetime.utcnow() - self._started_at).total_seconds()

    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get all debug information.

        Returns:
            Complete debug data including logs, trace, variables, API calls, and timing
        """
        return {
            "execution_id": self.execution_id,
            "plugin_id": self.plugin_id,
            "workspace_id": self.workspace_id,
            "logs": self.get_logs(),
            "trace": self.get_trace(),
            "steps": self.get_steps(),
            "variables": self.get_variables(),
            "api_calls": self.get_api_calls(),
            "step_timings": self.get_step_timings(),
            "total_execution_time": self.get_execution_time(),
        }

    def get_debug_data(self) -> Dict[str, Any]:
        """Alias for get_debug_info()"""
        return self.get_debug_info()
