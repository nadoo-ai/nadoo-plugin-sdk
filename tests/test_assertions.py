"""
Test new assertion methods
"""

import unittest
from nadoo_plugin import NadooPlugin, tool, parameter
from nadoo_plugin.testing import PluginTestCase


class TestPlugin(NadooPlugin):
    """Test plugin for assertion testing"""

    @tool(name="test_tool", description="Test tool")
    @parameter("input", type="string", required=True)
    def test_tool(self, input: str) -> dict:
        # Call various APIs
        self.api.tools.invoke(tool_name="web_search", parameters={"query": "test"})
        self.api.storage.set("cache_key", "cached_value")
        self.api.storage.get("cache_key")

        # Add trace event
        self.context.add_trace("custom_event", data={"status": "success"})

        # Start and complete a step
        self.context.start_step("processing")
        self.context.end_step()

        return {"result": input}


class TestNewAssertions(PluginTestCase):
    """Test newly implemented assertion methods"""

    plugin_class = TestPlugin

    def test_tool_called_with_parameters(self):
        """Test assertToolCalled with parameters"""
        result = self.execute_tool("test_tool", {"input": "test"})

        self.assertSuccess(result)
        self.assertToolCalled("web_search", parameters={"query": "test"})

    def test_tool_not_called(self):
        """Test assertToolNotCalled"""
        result = self.execute_tool("test_tool", {"input": "test"})

        self.assertSuccess(result)
        self.assertToolNotCalled("dangerous_tool")

    def test_storage_get(self):
        """Test assertStorageGet"""
        result = self.execute_tool("test_tool", {"input": "test"})

        self.assertSuccess(result)
        self.assertStorageSet("cache_key", "cached_value")
        self.assertStorageGet("cache_key")

    def test_step_started(self):
        """Test assertStepStarted"""
        result = self.execute_tool("test_tool", {"input": "test"})

        self.assertSuccess(result)
        self.assertStepStarted("processing")
        self.assertStepCompleted("processing")

    def test_trace_contains(self):
        """Test assertTraceContains"""
        result = self.execute_tool("test_tool", {"input": "test"})

        self.assertSuccess(result)
        self.assertTraceContains("custom_event", data={"status": "success"})


if __name__ == "__main__":
    unittest.main()
