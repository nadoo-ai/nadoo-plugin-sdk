"""
Unit tests for Hello World Plugin
"""

import unittest
from nadoo_plugin.testing import PluginTestCase
from nadoo_plugin.exceptions import PluginExecutionError
from main import HelloWorldPlugin


class TestHelloWorldPlugin(PluginTestCase):
    """Test cases for HelloWorldPlugin"""

    plugin_class = HelloWorldPlugin

    def test_greet_english(self):
        """Test greeting in English"""
        result = self.execute_tool("greet", {"name": "Alice", "language": "english"})

        self.assertSuccess(result)
        self.assertEqual(result["greeting"], "Hello, Alice! Welcome to Nadoo!")
        self.assertEqual(result["language"], "english")
        self.assertEqual(result["name"], "Alice")

        # Verify logging
        self.assertLogContains("Generating greeting for Alice in english", level="info")

        # Verify trace
        debug_data = self.get_debug_data()
        trace_events = [t["event"] for t in debug_data["trace"]]
        self.assertIn("greeting_generated", trace_events)

    def test_greet_spanish(self):
        """Test greeting in Spanish"""
        result = self.execute_tool("greet", {"name": "María", "language": "spanish"})

        self.assertSuccess(result)
        self.assertIn("¡Hola, María!", result["greeting"])
        self.assertEqual(result["language"], "spanish")

    def test_greet_french(self):
        """Test greeting in French"""
        result = self.execute_tool("greet", {"name": "Pierre", "language": "french"})

        self.assertSuccess(result)
        self.assertIn("Bonjour, Pierre!", result["greeting"])
        self.assertEqual(result["language"], "french")

    def test_greet_korean(self):
        """Test greeting in Korean"""
        result = self.execute_tool("greet", {"name": "지민", "language": "korean"})

        self.assertSuccess(result)
        self.assertIn("안녕하세요", result["greeting"])
        self.assertEqual(result["language"], "korean")

    def test_greet_invalid_language(self):
        """Test greeting with invalid language"""
        with self.assertRaises(PluginExecutionError) as context:
            self.execute_tool("greet", {"name": "Alice", "language": "german"})

        self.assertIn("must be one of", str(context.exception))
        self.assertIn("english", str(context.exception))

    def test_greet_default_language(self):
        """Test greeting with default language"""
        result = self.execute_tool("greet", {"name": "Bob"})

        self.assertSuccess(result)
        self.assertEqual(result["language"], "english")

    def test_echo_no_transform(self):
        """Test echo without transformation"""
        result = self.execute_tool("echo", {"text": "Hello World"})

        self.assertSuccess(result)
        self.assertEqual(result["result"], "Hello World")
        self.assertEqual(result["original"], "Hello World")
        self.assertEqual(result["transform"], "none")

        # Verify variables were watched
        self.assertVariableWatched("original_text", "Hello World")
        self.assertVariableWatched("transformed_text", "Hello World")

    def test_echo_uppercase(self):
        """Test echo with uppercase transformation"""
        result = self.execute_tool("echo", {"text": "hello world", "transform": "uppercase"})

        self.assertSuccess(result)
        self.assertEqual(result["result"], "HELLO WORLD")
        self.assertEqual(result["original"], "hello world")

    def test_echo_lowercase(self):
        """Test echo with lowercase transformation"""
        result = self.execute_tool("echo", {"text": "HELLO WORLD", "transform": "lowercase"})

        self.assertSuccess(result)
        self.assertEqual(result["result"], "hello world")

    def test_echo_reverse(self):
        """Test echo with reverse transformation"""
        result = self.execute_tool("echo", {"text": "Hello", "transform": "reverse"})

        self.assertSuccess(result)
        self.assertEqual(result["result"], "olleH")

    def test_echo_invalid_transform(self):
        """Test echo with invalid transformation"""
        with self.assertRaises(PluginExecutionError) as context:
            self.execute_tool("echo", {"text": "Hello", "transform": "invalid"})

        self.assertIn("must be one of", str(context.exception))

    def test_echo_text_too_long(self):
        """Test echo with text exceeding max length"""
        long_text = "a" * 1001  # Exceeds max_length=1000

        with self.assertRaises(PluginExecutionError) as context:
            self.execute_tool("echo", {"text": long_text})

        self.assertIn("must have length <=", str(context.exception))

    def test_echo_empty_text(self):
        """Test echo with empty text"""
        with self.assertRaises(PluginExecutionError) as context:
            self.execute_tool("echo", {"text": ""})

        self.assertIn("must have length >=", str(context.exception))

    def test_add_numbers_integers(self):
        """Test adding integers"""
        result = self.execute_tool("add_numbers", {"a": 5, "b": 3})

        self.assertSuccess(result)
        self.assertEqual(result["sum"], 8)
        self.assertEqual(result["a"], 5)
        self.assertEqual(result["b"], 3)

        # Verify variable was watched
        self.assertVariableWatched("result", 8)

    def test_add_numbers_floats(self):
        """Test adding floats"""
        result = self.execute_tool("add_numbers", {"a": 3.5, "b": 2.5})

        self.assertSuccess(result)
        self.assertEqual(result["sum"], 6.0)

    def test_add_numbers_negative(self):
        """Test adding negative numbers"""
        result = self.execute_tool("add_numbers", {"a": -5, "b": 3})

        self.assertSuccess(result)
        self.assertEqual(result["sum"], -2)

    def test_add_numbers_zero(self):
        """Test adding with zero"""
        result = self.execute_tool("add_numbers", {"a": 0, "b": 42})

        self.assertSuccess(result)
        self.assertEqual(result["sum"], 42)

    def test_debug_information(self):
        """Test that debug information is collected"""
        # Execute a tool
        self.execute_tool("greet", {"name": "Test", "language": "english"})

        # Get debug data
        debug_data = self.get_debug_data()

        # Verify debug data structure
        self.assertIn("logs", debug_data)
        self.assertIn("trace", debug_data)
        self.assertIn("steps", debug_data)
        self.assertIn("variables", debug_data)
        self.assertIn("api_calls", debug_data)

        # Verify logs exist
        self.assertGreater(len(debug_data["logs"]), 0)

        # Verify trace exists
        self.assertGreater(len(debug_data["trace"]), 0)


if __name__ == "__main__":
    unittest.main()
