# Nadoo Plugin SDK

[![PyPI version](https://badge.fury.io/py/nadoo-plugin-sdk.svg)](https://pypi.org/project/nadoo-plugin-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/nadoo-plugin-sdk.svg)](https://pypi.org/project/nadoo-plugin-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/nadoo-ai/nadoo-plugin-sdk/workflows/CI/badge.svg)](https://github.com/nadoo-ai/nadoo-plugin-sdk/actions)
[![codecov](https://codecov.io/gh/nadoo-ai/nadoo-plugin-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/nadoo-ai/nadoo-plugin-sdk)

**Official Python SDK for developing custom plugins for Nadoo AI Platform.**

Extend Nadoo with custom tools, integrate external APIs, and build reusable AI components using a simple decorator-based API.

## Features

- 🎯 **Simple API** - Decorator-based API for defining tools with minimal boilerplate
- 🤖 **Built-in LLM Access** - Invoke AI models configured in your workspace
- 📚 **Knowledge Integration** - Search and retrieve from knowledge bases
- 🐛 **Powerful Debugging** - Comprehensive logging, tracing, and variable watching

**Additional Capabilities:**
- 🔒 Type-safe with full runtime validation
- 🛠️ Rich CLI tooling for development lifecycle
- 🧪 Built-in testing utilities with PluginTestCase
- 🔄 Seamless workflow integration
- ⚡ Real-time performance tracking

## Installation

```bash
pip install nadoo-plugin-sdk
```

## Quick Start

### 1. Create a New Plugin

```bash
nadoo-plugin create my-awesome-plugin
cd my-awesome-plugin
```

### 2. Implement Your Plugin

```python
# main.py
from nadoo_plugin import NadooPlugin, tool, parameter

class MyPlugin(NadooPlugin):
    """My awesome plugin"""

    def on_initialize(self):
        """Called when plugin is loaded"""
        self.api_key = self.require_env("API_KEY")
        self.context.log("Plugin initialized!")

    @tool(
        name="process_text",
        description="Process text using AI"
    )
    @parameter("text", type="string", required=True, description="Text to process")
    @parameter("mode", type="string", default="standard", description="Processing mode")
    def process_text(self, text: str, mode: str = "standard") -> dict:
        """Process text and return results"""

        # Use Nadoo's LLM
        response = self.api.llm.invoke(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Process this text in {mode} mode: {text}"}
            ],
            temperature=0.7
        )

        return {
            "processed": response.content,
            "mode": mode,
            "tokens_used": response.usage["total_tokens"]
        }
```

### 3. Test Your Plugin

```bash
nadoo-plugin test --tool process_text --params '{"text": "Hello World"}'
```

### 4. Build and Deploy

```bash
nadoo-plugin build
# Creates: my-awesome-plugin-1.0.0.nadoo-plugin

# Upload to Nadoo workspace
nadoo-plugin install my-awesome-plugin-1.0.0.nadoo-plugin --workspace my-workspace
```

## Core Concepts

### Plugin Class

All plugins inherit from `NadooPlugin`:

```python
from nadoo_plugin import NadooPlugin

class MyPlugin(NadooPlugin):
    def on_initialize(self):
        """Optional: Initialize plugin"""
        pass

    def on_finalize(self):
        """Optional: Cleanup before shutdown"""
        pass
```

### Tools

Tools are functions that can be called by workflows:

```python
@tool(name="my_tool", description="Does something useful")
@parameter("input", type="string", required=True)
def my_tool(self, input: str) -> dict:
    return {"result": input.upper()}
```

### Context

Access execution context and logging:

```python
def my_tool(self, input: str) -> dict:
    # Logging (supports debug, info, warn, error)
    self.context.log("Processing input", level="info")
    self.context.warn("This might take a while")
    self.context.error("Something went wrong")
    self.context.debug("Debug information")

    # Execution Steps
    self.context.start_step("fetch_data")
    # ... do work ...
    self.context.end_step()  # Automatically tracks duration

    # Variable Watching
    self.context.watch_variable("input_length", len(input), metadata={"type": "metric"})

    # Trace Events
    self.context.add_trace("custom_event", data={"key": "value"})

    return {"result": "done"}
```

### Internal APIs

Access Nadoo services from your plugin:

#### LLM API

```python
# Invoke AI models
response = self.api.llm.invoke(
    messages=[{"role": "user", "content": "Hello!"}],
    temperature=0.7,
    max_tokens=100
)

print(response.content)  # AI response
print(response.model_name)  # Model used
print(response.usage)  # Token usage
```

#### Tools API

```python
# Call other tools
result = self.api.tools.invoke(
    tool_name="web_search",
    parameters={"query": "AI news"}
)
```

#### Knowledge Base API

```python
# Search knowledge bases
results = self.api.knowledge.search(
    knowledge_base_uuid="kb-uuid-here",
    query="How to use plugins?",
    top_k=5
)

for result in results:
    print(result.content, result.score)
```

#### Storage API

```python
# Store persistent data
self.api.storage.set("my_key", {"data": "value"}, ttl=3600)

# Retrieve data
value = self.api.storage.get("my_key")

# Delete data
self.api.storage.delete("my_key")
```

## manifest.yaml

Every plugin needs a `manifest.yaml`:

```yaml
name: my-awesome-plugin
display_name: My Awesome Plugin
version: 1.0.0
author: Your Name
description: A plugin that does awesome things

# SDK version requirement
# Supported formats:
#   "0.1.0" - Exact version
#   ">=0.1.0" - Greater than or equal
#   "^0.1.0" - Compatible (allows minor/patch updates, same major)
#   "~0.1.0" - Approximately (allows patch updates only)
sdk_version: ">=0.1.0"

entry_point: main.py
python_version: ">=3.9"

permissions:
  - llm_access
  - storage

environment_variables:
  - name: API_KEY
    required: true
    description: Your API key

tools:
  - name: process_text
    description: Process text using AI
    parameters:
      - name: text
        type: string
        required: true
      - name: mode
        type: string
        required: false
        default: standard

resource_limits:
  memory_mb: 100
  timeout_seconds: 30

homepage: https://github.com/user/my-plugin
license: MIT
keywords:
  - text
  - ai
```

## CLI Commands

```bash
# Create new plugin
nadoo-plugin create <name>

# Validate plugin
nadoo-plugin validate

# Test plugin locally
nadoo-plugin test --tool <tool-name> --params <json>

# Build plugin package
nadoo-plugin build

# Install to workspace
nadoo-plugin install <package-file> --workspace <workspace-id>
```

## Testing Your Plugin

The SDK provides comprehensive testing utilities for unit testing plugins.

### Basic Test Example

```python
# test_my_plugin.py
from nadoo_plugin.testing import PluginTestCase
from my_plugin import MyPlugin

class TestMyPlugin(PluginTestCase):
    plugin_class = MyPlugin

    def test_process_text(self):
        # Mock LLM response
        self.mock_llm_response("Processed text result")

        # Execute tool
        result = self.execute_tool("process_text", {
            "text": "Hello World",
            "mode": "standard"
        })

        # Assertions
        self.assertSuccess(result)
        self.assertHasKey(result, "processed")
        self.assertEqual(result["processed"], "Processed text result")

        # Verify LLM was called
        self.assertLLMCalled(temperature=0.7)
```

### Available Mock Helpers

```python
# Mock LLM responses
self.mock_llm_response("AI response", model_name="gpt-4")

# Mock tool responses
self.mock_tool_response("web_search", {"results": [...]})

# Mock knowledge search results
self.mock_knowledge_results([
    {"content": "Result 1", "score": 0.9},
    {"content": "Result 2", "score": 0.8}
])

# Pre-populate storage
self.set_storage("cache_key", "cached_value")
```

### Available Assertions

```python
# Result assertions
self.assertSuccess(result)
self.assertError(result, error_msg="Expected error")
self.assertHasKey(result, "key_name")
self.assertEqual(result["key"], expected_value)
self.assertIn("substring", result["text"])

# API call assertions
self.assertLLMCalled(temperature=0.7, max_tokens=500)
self.assertLLMNotCalled()
self.assertToolCalled("web_search", parameters={"query": "test"})
self.assertToolNotCalled("dangerous_tool")
self.assertStorageSet("key", "value")
self.assertStorageGet("key")
self.assertKnowledgeSearchCalled(query="test", top_k=5)

# Context assertions
self.assertLogContains("message", level="info")
self.assertVariableWatched("variable_name", value=123)
self.assertStepStarted("step_name")
self.assertStepCompleted("step_name")
self.assertTraceContains("event_name")

# Debug output
self.print_debug()  # Print all debug information
debug_data = self.get_debug_data()  # Get debug data dict
```

### Running Tests

```bash
# Run tests
python -m pytest test_my_plugin.py -v

# Run with coverage
python -m pytest --cov=my_plugin test_my_plugin.py
```

## Decorators

### @validator Decorator

Validate tool parameters with declarative constraints:

```python
from nadoo_plugin import NadooPlugin, tool, parameter, validator

class MyPlugin(NadooPlugin):
    @tool(name="process_text", description="Process text")
    @parameter("text", type="string", required=True)
    @parameter("count", type="integer", default=5)
    @validator("text", min_length=10, max_length=1000, pattern=r'^[a-zA-Z0-9\s]+$')
    @validator("count", min_value=1, max_value=100)
    def process_text(self, text: str, count: int = 5) -> dict:
        # text and count are already validated
        return {"result": text, "count": count}

    @tool(name="format_text", description="Format text")
    @parameter("format", type="string", required=True)
    @validator("format", allowed_values=["upper", "lower", "title", "capitalize"])
    def format_text(self, text: str, format: str) -> dict:
        # format is validated to be one of the allowed values
        formatters = {
            "upper": text.upper,
            "lower": text.lower,
            "title": text.title,
            "capitalize": text.capitalize,
        }
        return {"formatted": formatters[format]()}
```

Supported validator constraints:

- `allowed_values`: List of allowed values
- `min_value`, `max_value`: Numeric range (for int/float)
- `min_length`, `max_length`: String/array length
- `pattern`: Regex pattern (for strings)

### @validate_parameters Decorator

For advanced validation with custom schemas:

```python
from nadoo_plugin import NadooPlugin, tool, validate_parameters

class MyPlugin(NadooPlugin):
    @tool(name="create_user", description="Create a user")
    @validate_parameters({
        "email": {"type": "string", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
        "age": {"type": "number", "min": 0, "max": 150},
        "name": {"type": "string", "min_length": 2, "max_length": 100}
    })
    def create_user(self, email: str, age: int, name: str) -> dict:
        return {"success": True, "user": {"email": email, "age": age, "name": name}}
```

### @retry Decorator

Automatically retry failed tool executions with exponential backoff:

```python
from nadoo_plugin import NadooPlugin, tool, retry

class MyPlugin(NadooPlugin):
    @tool(name="fetch_data", description="Fetch data from API")
    @retry(max_attempts=3, delay=1.0, backoff=2.0)
    def fetch_data(self, url: str) -> dict:
        """
        Will retry up to 3 times with exponential backoff:
        - First retry: 1.0s delay
        - Second retry: 2.0s delay
        - Third retry: 4.0s delay
        """
        import httpx
        response = httpx.get(url, timeout=5.0)
        response.raise_for_status()
        return {"data": response.json()}
```

### @permission_required Decorator

Check permissions before tool execution:

```python
from nadoo_plugin import NadooPlugin, tool, permission_required

class MyPlugin(NadooPlugin):
    @tool(name="analyze_data", description="Analyze data")
    @permission_required("llm_access", "storage")
    def analyze_data(self, data: str) -> dict:
        # Only executes if plugin has both llm_access and storage permissions
        response = self.api.llm.invoke([{"role": "user", "content": data}])
        self.api.storage.set("last_analysis", response.content)
        return {"result": response.content}
```

## Real-time Debugging

The SDK includes a comprehensive debugging system that streams execution data in real-time via WebSocket.

### Debug Data Includes:

- **Logs** - All log messages with timestamps and levels
- **Execution Trace** - Timeline of events and steps
- **Variables** - Watched variables with values and metadata
- **API Calls** - All API calls with duration and success status
- **Performance Metrics** - Step durations, API timings, success rates

### Using the Debug Inspector

Connect to the debug WebSocket endpoint:

```
ws://backend-url/ws/plugin-debug/{execution_uuid}
```

The frontend includes a built-in `PluginDebugInspector` component with:
- Log viewer with filtering
- Execution trace timeline
- Variable inspector
- API calls timeline
- Performance metrics dashboard

## Examples

See the `/examples` directory for complete plugin examples:

- **hello-world** - Basic plugin demonstrating core features and decorators
- **llm-summarizer** - Advanced LLM integration with caching, batch processing, and KB search
  - Text summarization with multiple styles
  - Keyword extraction
  - Question answering with Knowledge Base integration
  - Batch summarization with error handling

## Documentation

📖 **Full Documentation**: https://docs.nadoo.ai/plugin-sdk/overview

- [Quick Start Guide](https://docs.nadoo.ai/plugin-sdk/quickstart)
- [API Reference](https://docs.nadoo.ai/plugin-sdk/api)
- [Examples](https://docs.nadoo.ai/plugin-sdk/examples)
- [Best Practices](https://docs.nadoo.ai/plugin-sdk/best-practices)

## Support

- 🐛 **Issues**: https://github.com/nadoo-ai/nadoo-plugin-sdk/issues
- 💬 **Discussions**: https://github.com/nadoo-ai/nadoo-plugin-sdk/discussions
- 📧 **Email**: support@nadoo.ai

## License

MIT License - see LICENSE file for details
