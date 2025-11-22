"""
Base test case class for plugin testing
"""

import unittest
from typing import Any, Dict, List, Optional, Type

from ..plugin import NadooPlugin
from .mocks import MockContext, MockAPIClient


class PluginTestCase(unittest.TestCase):
    """
    Base test case for plugin testing

    Provides helper methods for plugin initialization and assertion.

    Example:
        class TestMyPlugin(PluginTestCase):
            plugin_class = MyPlugin

            def test_my_tool(self):
                # Plugin is already initialized in setUp()
                result = self.plugin.execute("my_tool", {"input": "test"})
                self.assertSuccess(result)
                self.assertEqual(result["output"], "expected")
    """

    # Subclasses should set this
    plugin_class: Optional[Type[NadooPlugin]] = None

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()

        # Create mock context and API
        self.context = MockContext()
        self.api = MockAPIClient(self.context)

        # Initialize plugin if class is specified
        if self.plugin_class:
            self.plugin = self.plugin_class()
            self.init_plugin(self.plugin, context=self.context, api=self.api)

    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, "plugin"):
            self.plugin.finalize()
        if hasattr(self, "api"):
            self.api.close()
        super().tearDown()

    def init_plugin(
        self,
        plugin: NadooPlugin,
        context: Optional[MockContext] = None,
        api: Optional[MockAPIClient] = None,
    ):
        """
        Initialize plugin with mock context and API

        Args:
            plugin: Plugin instance
            context: Mock context (uses self.context if not provided)
            api: Mock API client (uses self.api if not provided)
        """
        ctx = context or self.context
        api_client = api or self.api

        plugin.initialize(context=ctx, api=api_client)

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool on the plugin

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters

        Returns:
            Tool result
        """
        if not hasattr(self, "plugin"):
            raise RuntimeError("Plugin not initialized. Set plugin_class or call init_plugin()")

        return self.plugin.execute(tool_name, parameters)

    # ==================== Mock Response Helpers ====================

    def mock_llm_response(self, content: str, model_name: str = "gpt-4", usage: Optional[Dict] = None):
        """
        Set the next LLM response

        Args:
            content: Response content
            model_name: Model name
            usage: Token usage dict

        Example:
            self.mock_llm_response("This is a test response")
            result = self.plugin.execute("summarize", {"text": "..."})
        """
        self.api.llm.set_response(content, model_name, usage)

    def mock_tool_response(self, tool_name: str, result: Any):
        """
        Set response for a specific tool

        Args:
            tool_name: Tool name
            result: Tool result

        Example:
            self.mock_tool_response("web_search", {"results": [...]})
            result = self.plugin.execute("search_and_process", {"query": "..."})
        """
        self.api.tools.set_tool_response(tool_name, result)

    def mock_knowledge_results(self, results: List[Dict[str, Any]]):
        """
        Set knowledge search results

        Args:
            results: List of search result dicts

        Example:
            self.mock_knowledge_results([
                {"content": "Result 1", "score": 0.9},
                {"content": "Result 2", "score": 0.8}
            ])
        """
        self.api.knowledge.set_search_results(results)

    def set_storage(self, key: str, value: Any):
        """
        Pre-populate storage

        Args:
            key: Storage key
            value: Storage value

        Example:
            self.set_storage("config", {"enabled": True})
        """
        self.api.storage.set(key, value)

    # ==================== Assertion Helpers ====================

    def assertSuccess(self, result: Dict[str, Any], msg: Optional[str] = None):
        """
        Assert that result indicates success

        Args:
            result: Tool result
            msg: Optional assertion message
        """
        if "success" in result:
            self.assertTrue(result["success"], msg or f"Expected success=True, got {result}")
        # If no 'success' field, just check it's not an error
        self.assertNotIn("error", result, msg or f"Result contains error: {result.get('error')}")

    def assertError(self, result: Dict[str, Any], error_msg: Optional[str] = None):
        """
        Assert that result contains an error

        Args:
            result: Tool result
            error_msg: Expected error message (substring match)
        """
        self.assertTrue(
            "error" in result or (result.get("success") is False), f"Expected error in result, got {result}"
        )

        if error_msg:
            actual_error = result.get("error", "")
            self.assertIn(error_msg, str(actual_error), f"Expected error message containing '{error_msg}'")

    def assertHasKey(self, result: Dict[str, Any], key: str, msg: Optional[str] = None):
        """Assert that result has a specific key"""
        self.assertIn(key, result, msg or f"Expected key '{key}' in result")

    def assertLLMCalled(self, messages: Optional[List[Dict]] = None, **kwargs):
        """
        Assert that LLM was called

        Args:
            messages: Expected messages (optional)
            **kwargs: Expected keyword arguments

        Example:
            self.assertLLMCalled(temperature=0.7)
        """
        self.api.llm.assert_called_with(messages, **kwargs)

    def assertLLMNotCalled(self):
        """Assert that LLM was not called"""
        history = self.api.llm.get_call_history()
        self.assertEqual(len(history), 0, f"Expected LLM not to be called, but it was called {len(history)} times")

    def assertToolCalled(self, tool_name: str, parameters: Optional[Dict[str, Any]] = None):
        """
        Assert that a tool was invoked

        Args:
            tool_name: Tool name
            parameters: Expected parameters (optional)

        Example:
            self.assertToolCalled("web_search")
            self.assertToolCalled("web_search", parameters={"query": "test"})
        """
        history = self.api.tools.get_call_history()
        tool_names = [call.get("tool_name") for call in history]
        self.assertIn(tool_name, tool_names, f"Expected tool '{tool_name}' to be called")

        # If parameters specified, verify them
        if parameters is not None:
            matching_calls = [call for call in history if call.get("tool_name") == tool_name]
            if matching_calls:
                last_call = matching_calls[-1]
                actual_params = last_call.get("parameters", {})
                for key, expected_value in parameters.items():
                    self.assertEqual(
                        actual_params.get(key),
                        expected_value,
                        f"Expected tool '{tool_name}' parameter '{key}' to be {expected_value}, got {actual_params.get(key)}"
                    )

    def assertToolNotCalled(self, tool_name: str):
        """
        Assert that a tool was NOT invoked

        Args:
            tool_name: Tool name

        Example:
            self.assertToolNotCalled("dangerous_tool")
        """
        history = self.api.tools.get_call_history()
        tool_names = [call.get("tool_name") for call in history]
        self.assertNotIn(tool_name, tool_names, f"Expected tool '{tool_name}' NOT to be called, but it was called")

    def assertStorageSet(self, key: str, value: Optional[Any] = None):
        """
        Assert that storage.set was called

        Args:
            key: Storage key
            value: Expected value (optional)

        Example:
            self.assertStorageSet("cache_key", "cached_value")
        """
        history = self.api.storage.get_call_history()
        set_calls = [call for call in history if call.get("operation") == "set" and call.get("key") == key]

        self.assertGreater(len(set_calls), 0, f"Expected storage.set('{key}') to be called")

        if value is not None:
            actual_value = set_calls[-1].get("value")
            self.assertEqual(actual_value, value, f"Expected storage value {value}, got {actual_value}")

    def assertStorageGet(self, key: str):
        """
        Assert that storage.get was called

        Args:
            key: Storage key

        Example:
            self.assertStorageGet("config_key")
        """
        history = self.api.storage.get_call_history()
        get_calls = [call for call in history if call.get("operation") == "get" and call.get("key") == key]

        self.assertGreater(len(get_calls), 0, f"Expected storage.get('{key}') to be called")

    def assertKnowledgeSearchCalled(self, query: Optional[str] = None, top_k: Optional[int] = None):
        """
        Assert that knowledge base search was called

        Args:
            query: Expected query (optional, substring match)
            top_k: Expected top_k value (optional)

        Example:
            self.assertKnowledgeSearchCalled(query="test", top_k=5)
        """
        history = self.api.knowledge.get_call_history()
        self.assertGreater(len(history), 0, "Expected knowledge search to be called")

        if query is not None or top_k is not None:
            last_call = history[-1]

            if query is not None:
                actual_query = last_call.get("query", "")
                self.assertIn(query, actual_query, f"Expected query to contain '{query}', got '{actual_query}'")

            if top_k is not None:
                actual_top_k = last_call.get("top_k")
                self.assertEqual(actual_top_k, top_k, f"Expected top_k={top_k}, got {actual_top_k}")

    def assertLogContains(self, message: str, level: Optional[str] = None):
        """
        Assert that context logs contain a message

        Args:
            message: Message substring to search for
            level: Log level (optional)

        Example:
            self.assertLogContains("Processing started", level="info")
        """
        logs = self.context.get_logs()
        matching_logs = [log for log in logs if message in log.get("message", "")]

        if level:
            matching_logs = [log for log in matching_logs if log.get("level") == level]

        self.assertGreater(
            len(matching_logs), 0, f"Expected log message containing '{message}'" + (f" at level '{level}'" if level else "")
        )

    def assertVariableWatched(self, name: str, value: Optional[Any] = None):
        """
        Assert that a variable was watched

        Args:
            name: Variable name
            value: Expected value (optional)

        Example:
            self.assertVariableWatched("result_count", 5)
        """
        variables = self.context.get_variables()
        self.assertIn(name, variables, f"Expected variable '{name}' to be watched")

        if value is not None:
            actual_value = variables[name].get("value")
            self.assertEqual(actual_value, value, f"Expected variable value {value}, got {actual_value}")

    def assertStepStarted(self, step_name: str):
        """
        Assert that a step was started

        Args:
            step_name: Step name

        Example:
            self.assertStepStarted("data_processing")
        """
        steps = self.context.get_steps()
        step_names = [step.get("step_name") for step in steps]
        self.assertIn(step_name, step_names, f"Expected step '{step_name}' to be started")

    def assertStepCompleted(self, step_name: str):
        """
        Assert that a step was completed

        Args:
            step_name: Step name

        Example:
            self.assertStepCompleted("data_processing")
        """
        steps = self.context.get_steps()
        step_names = [step.get("step_name") for step in steps]
        self.assertIn(step_name, step_names, f"Expected step '{step_name}' to be completed")

        # Check that step has duration (was ended)
        matching_steps = [step for step in steps if step.get("step_name") == step_name]
        self.assertIsNotNone(matching_steps[-1].get("duration"), f"Step '{step_name}' was not ended")

    def assertTraceContains(self, event_name: str, data: Optional[Dict[str, Any]] = None):
        """
        Assert that trace contains a specific event

        Args:
            event_name: Event name
            data: Expected event data (optional, partial match)

        Example:
            self.assertTraceContains("custom_event")
            self.assertTraceContains("api_call", data={"status": "success"})
        """
        trace = self.context.get_trace()
        event_names = [event.get("event") for event in trace]
        self.assertIn(event_name, event_names, f"Expected trace event '{event_name}'")

        # If data specified, verify it
        if data is not None:
            matching_events = [event for event in trace if event.get("event") == event_name]
            if matching_events:
                last_event = matching_events[-1]
                event_data = last_event.get("data", {})
                if not isinstance(event_data, dict):
                    self.fail(f"Trace event '{event_name}' data is not a dict: {event_data}")
                for key, expected_value in data.items():
                    self.assertEqual(
                        event_data.get(key),
                        expected_value,
                        f"Expected trace event '{event_name}' data '{key}' to be {expected_value}, got {event_data.get(key)}"
                    )

    def get_debug_data(self) -> Dict[str, Any]:
        """
        Get all debug data from context

        Returns:
            Debug data dict

        Example:
            debug_data = self.get_debug_data()
            print(debug_data["logs"])
        """
        return self.context.get_debug_data()

    def print_debug(self):
        """Print debug information (useful for debugging tests)"""
        debug_data = self.get_debug_data()

        print("\n=== Debug Information ===")
        print(f"\nLogs ({len(debug_data['logs'])}):")
        for log in debug_data["logs"]:
            print(f"  [{log['level'].upper()}] {log['message']}")

        print(f"\nSteps ({len(debug_data['steps'])}):")
        for step in debug_data["steps"]:
            duration = step.get("duration", "N/A")
            print(f"  {step['step_name']}: {duration}s")

        print(f"\nVariables ({len(debug_data['variables'])}):")
        for name, var in debug_data["variables"].items():
            print(f"  {name} = {var['value']} ({var['value_type']})")

        print(f"\nAPI Calls ({len(debug_data['api_calls'])}):")
        for call in debug_data["api_calls"]:
            status = "✓" if call["success"] else "✗"
            print(f"  {status} {call['api_type']}: {call['endpoint']} ({call['duration']:.3f}s)")

        print("\n========================\n")
