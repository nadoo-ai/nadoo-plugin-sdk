"""
Mock objects for testing plugins
"""

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

from ..context import PluginContext
from ..api.llm import LLMResponse
from ..api.knowledge import KnowledgeSearchResult


class MockContext(PluginContext):
    """
    Mock context for testing plugins without real backend

    Example:
        context = MockContext(
            execution_id="test-exec",
            plugin_id="test-plugin",
            workspace_id="test-workspace"
        )
    """

    def __init__(
        self,
        execution_id: str = "test-execution",
        plugin_id: str = "test-plugin",
        workspace_id: str = "test-workspace",
        user_id: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        debug_mode: bool = True,
        **kwargs,
    ):
        # Provide all required permissions by default for testing
        if permissions is None:
            permissions = ["llm_access", "tool_invocation", "knowledge_access", "storage"]

        super().__init__(
            execution_id=execution_id,
            plugin_id=plugin_id,
            workspace_id=workspace_id,
            user_id=user_id,
            permissions=permissions,
            debug_mode=debug_mode,
            **kwargs,
        )


class MockLLMClient:
    """
    Mock LLM client for testing

    Example:
        llm = MockLLMClient()
        llm.set_response("This is a test response")

        response = llm.invoke(messages=[...])
        assert response.content == "This is a test response"
    """

    def __init__(self, context: Optional[PluginContext] = None):
        self.context = context or MockContext()
        self._responses = []
        self._call_history = []

    def set_response(self, content: str, model_name: str = "gpt-4", usage: Optional[Dict] = None):
        """Set the next response to return"""
        if usage is None:
            usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}

        self._responses.append(
            LLMResponse(
                content=content,
                model_uuid="test-model-uuid",
                model_name=model_name,
                model_id=model_name,
                provider="openai",
                usage=usage,
            )
        )

    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Mock LLM invocation"""
        import time

        start_time = time.time()

        # Record call
        self._call_history.append({"messages": messages, "kwargs": kwargs})

        # Return preset response or default
        if self._responses:
            response = self._responses.pop(0)
        else:
            # Default response
            response = LLMResponse(
                content="Mock LLM response",
                model_uuid="test-model-uuid",
                model_name="gpt-4",
                model_id="gpt-4",
                provider="openai",
                usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            )

        # Record API call to context
        duration = time.time() - start_time
        if self.context:
            self.context.record_api_call(
                api_type="llm",
                endpoint="/internal-api/plugin/invoke/llm",
                parameters={"messages": messages, **kwargs},
                result={"content": response.content, "model": response.model_name},
                duration=duration,
            )

        return response

    def get_call_history(self) -> List[Dict]:
        """Get history of all invoke calls"""
        return self._call_history

    def assert_called_with(self, messages: Optional[List[Dict]] = None, **kwargs):
        """Assert that invoke was called with specific arguments"""
        if not self._call_history:
            raise AssertionError("LLM client was not called")

        last_call = self._call_history[-1]

        if messages is not None:
            assert last_call["messages"] == messages, f"Expected messages {messages}, got {last_call['messages']}"

        for key, value in kwargs.items():
            assert (
                last_call["kwargs"].get(key) == value
            ), f"Expected {key}={value}, got {last_call['kwargs'].get(key)}"

    def close(self):
        """Mock close method"""
        pass


class MockToolsClient:
    """Mock Tools client for testing"""

    def __init__(self, context: Optional[PluginContext] = None):
        self.context = context or MockContext()
        self._responses = {}
        self._call_history = []

    def set_tool_response(self, tool_name: str, result: Any):
        """Set response for a specific tool"""
        self._responses[tool_name] = result

    def invoke(self, tool_uuid: Optional[str] = None, tool_name: Optional[str] = None, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Mock tool invocation"""
        identifier = tool_name or tool_uuid

        # Record call
        self._call_history.append({"tool_uuid": tool_uuid, "tool_name": tool_name, "parameters": parameters})

        # Return preset response or default
        if tool_name and tool_name in self._responses:
            return self._responses[tool_name]

        return {"success": True, "result": "Mock tool result"}

    def get_call_history(self) -> List[Dict]:
        """Get history of all invoke calls"""
        return self._call_history

    def close(self):
        """Mock close method"""
        pass


class MockKnowledgeClient:
    """Mock Knowledge client for testing"""

    def __init__(self, context: Optional[PluginContext] = None):
        self.context = context or MockContext()
        self._results = []
        self._call_history = []

    def set_search_results(self, results: List[Dict[str, Any]]):
        """Set search results to return"""
        self._results = [
            KnowledgeSearchResult(
                chunk_id=r.get("chunk_id", "chunk-1"),
                content=r.get("content", ""),
                score=r.get("score", 0.9),
                metadata=r.get("metadata", {}),
            )
            for r in results
        ]

    def search(
        self, knowledge_base_uuid: str, query: str, top_k: int = 5, score_threshold: float = 0.0
    ) -> List[KnowledgeSearchResult]:
        """Mock knowledge search"""
        # Record call
        self._call_history.append(
            {"knowledge_base_uuid": knowledge_base_uuid, "query": query, "top_k": top_k, "score_threshold": score_threshold}
        )

        # Return preset results or default
        if self._results:
            return self._results[:top_k]

        # Default results
        return [
            KnowledgeSearchResult(
                chunk_id="chunk-1", content="Mock search result 1", score=0.95, metadata={"source": "test"}
            ),
            KnowledgeSearchResult(
                chunk_id="chunk-2", content="Mock search result 2", score=0.85, metadata={"source": "test"}
            ),
        ]

    def get_call_history(self) -> List[Dict]:
        """Get history of all search calls"""
        return self._call_history

    def close(self):
        """Mock close method"""
        pass


class MockStorageClient:
    """Mock Storage client for testing"""

    def __init__(self, context: Optional[PluginContext] = None):
        self.context = context or MockContext()
        self._storage = {}
        self._call_history = []

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Mock storage set"""
        import time

        start_time = time.time()
        self._storage[key] = value
        self._call_history.append({"operation": "set", "key": key, "value": value, "ttl": ttl})

        # Record API call to context
        duration = time.time() - start_time
        if self.context:
            self.context.record_api_call(
                api_type="storage",
                endpoint="/internal-api/plugin/storage/set",
                parameters={"key": key, "ttl": ttl},
                result={"success": True},
                duration=duration,
            )

        return True

    def get(self, key: str, default: Any = None) -> Any:
        """Mock storage get"""
        self._call_history.append({"operation": "get", "key": key})
        return self._storage.get(key, default)

    def delete(self, key: str) -> bool:
        """Mock storage delete"""
        self._call_history.append({"operation": "delete", "key": key})
        if key in self._storage:
            del self._storage[key]
            return True
        return False

    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """Mock storage list keys"""
        self._call_history.append({"operation": "list_keys", "prefix": prefix})

        keys = list(self._storage.keys())
        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]
        return keys

    def get_call_history(self) -> List[Dict]:
        """Get history of all storage calls"""
        return self._call_history

    def clear(self):
        """Clear all stored data"""
        self._storage.clear()

    def close(self):
        """Mock close method"""
        pass


class MockAPIClient:
    """
    Mock Internal API client

    Example:
        api = MockAPIClient()
        api.llm.set_response("Test response")

        response = api.llm.invoke(messages=[...])
        assert response.content == "Test response"
    """

    def __init__(self, context: Optional[PluginContext] = None):
        self.context = context or MockContext()
        self.llm = MockLLMClient(self.context)
        self.tools = MockToolsClient(self.context)
        self.knowledge = MockKnowledgeClient(self.context)
        self.storage = MockStorageClient(self.context)

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
