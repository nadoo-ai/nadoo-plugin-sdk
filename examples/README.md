# Nadoo Plugin Examples

This directory contains example plugins demonstrating various features of the Nadoo Plugin SDK.

## Available Examples

### 1. [hello-world](./hello-world/) - Beginner

**What it demonstrates:**
- Basic plugin structure
- Tool definition with `@tool` decorator
- Parameter validation with `@parameter` and `@validator`
- Context usage for logging
- Multi-language support
- Simple transformations

**Tools:**
- `greet` - Generate greetings in multiple languages
- `echo` - Echo text with transformations
- `add_numbers` - Simple arithmetic

**Best for:** Learning plugin basics, understanding decorator patterns

**Complexity:** ⭐ (Beginner)

---

### 2. [llm-summarizer](./llm-summarizer/) - Intermediate

**What it demonstrates:**
- LLM integration via Internal API
- Permission management (`@permission_required`)
- Intelligent caching with Storage API
- Knowledge base integration
- Batch processing
- Step tracking and debugging
- Error handling patterns

**Tools:**
- `summarize` - Text summarization with caching
- `extract_keywords` - Keyword extraction
- `answer_question` - Q&A with KB integration
- `batch_summarize` - Batch processing

**Best for:** Building AI-powered plugins, understanding API integration

**Complexity:** ⭐⭐⭐ (Intermediate)

---

## Learning Path

We recommend following this order:

1. **Start with hello-world** - Understand basic concepts
   - Read [hello-world/README.md](./hello-world/README.md)
   - Study [hello-world/main.py](./hello-world/main.py)
   - Run tests: `cd hello-world && python test_hello_world.py`

2. **Move to llm-summarizer** - Learn advanced patterns
   - Read [llm-summarizer/README.md](./llm-summarizer/README.md)
   - Study [llm-summarizer/main.py](./llm-summarizer/main.py)
   - Run tests: `cd llm-summarizer && python test_llm_summarizer.py`

3. **Create your own plugin**
   - Use `nadoo plugin create` to scaffold a new plugin
   - Refer to these examples for patterns
   - Read the full [SDK Documentation](../README.md)

## Running Examples

### Running Tests

Each example includes comprehensive unit tests:

```bash
# Hello World
cd examples/hello-world
python -m pytest test_hello_world.py -v

# LLM Summarizer
cd examples/llm-summarizer
python -m pytest test_llm_summarizer.py -v
```

### Installing Examples as Plugins

You can install these examples as actual plugins in your Nadoo workspace:

```bash
# Install Nadoo CLI
pip install nadoo-cli

# Package and install
cd examples/hello-world
nadoo plugin package
nadoo plugin install hello-world-1.0.0.zip

# Enable in workspace
nadoo plugin enable hello-world
```

## Common Patterns

### 1. Tool Definition

```python
from nadoo_plugin import NadooPlugin, tool, parameter, validator

class MyPlugin(NadooPlugin):
    @tool(name="my_tool", description="Does something useful")
    @parameter("input", type="string", required=True, description="Input text")
    @validator("input", min_length=1, max_length=1000)
    def my_tool(self, input: str) -> dict:
        return {"success": True, "result": input.upper()}
```

### 2. LLM Integration

```python
@permission_required("llm_access")
def use_llm(self, prompt: str) -> dict:
    response = self.api.llm.invoke(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return {"response": response.content}
```

### 3. Caching Pattern

```python
@permission_required("storage")
def cached_operation(self, input_data: str) -> dict:
    # Check cache
    cache_key = f"op:{hash(input_data)}"
    cached = self.api.storage.get(cache_key)
    if cached:
        return cached

    # Perform operation
    result = expensive_operation(input_data)

    # Cache with 1 hour TTL
    self.api.storage.set(cache_key, result, ttl=3600)
    return result
```

### 4. Knowledge Base Search

```python
@permission_required("knowledge_access")
def search_knowledge(self, query: str, kb_uuid: str) -> dict:
    results = self.api.knowledge.search(
        knowledge_base_uuid=kb_uuid,
        query=query,
        top_k=5,
        score_threshold=0.7
    )

    return {
        "results": [
            {
                "content": r.content,
                "score": r.score,
                "metadata": r.metadata
            }
            for r in results
        ]
    }
```

### 5. Debug Instrumentation

```python
def instrumented_operation(self):
    # Start tracking
    self.context.start_step("operation")
    self.context.info("Starting operation")

    # Watch variables
    self.context.watch_variable("input_size", len(data))

    # Trace events
    self.context.trace("processing_started", {"mode": "fast"})

    # Do work...

    # End tracking
    self.context.end_step("operation")
```

### 6. Testing Pattern

```python
from nadoo_plugin.testing import PluginTestCase

class TestMyPlugin(PluginTestCase):
    plugin_class = MyPlugin

    def test_my_tool(self):
        # Mock LLM if needed
        self.mock_llm_response("Mocked response")

        # Execute tool
        result = self.execute_tool("my_tool", {"input": "test"})

        # Assert results
        self.assertSuccess(result)
        self.assertHasKey(result, "output")

        # Verify API calls
        self.assertLLMCalled()
```

## File Structure

Each example follows this structure:

```
example-name/
├── main.py              # Plugin implementation
├── manifest.yaml        # Plugin metadata
├── test_*.py           # Unit tests
└── README.md           # Documentation
```

## Key SDK Components Used

### Decorators
- `@tool` - Define plugin tools
- `@parameter` - Define tool parameters
- `@validator` - Validate parameter values
- `@permission_required` - Require permissions
- `@retry` - Retry on failure

### Context API
- `context.info/warn/error()` - Logging
- `context.trace()` - Execution tracing
- `context.start_step() / end_step()` - Step timing
- `context.watch_variable()` - Variable snapshots
- `context.require_permission()` - Permission checks

### Internal APIs
- `api.llm.invoke()` - LLM invocation
- `api.tools.invoke()` - Tool invocation
- `api.knowledge.search()` - Knowledge base search
- `api.storage.get/set/delete()` - Key-value storage

### Testing Utilities
- `PluginTestCase` - Base test class
- `MockContext` - Mock execution context
- `MockAPIClient` - Mock Internal API
- Custom assertions (assertSuccess, assertLLMCalled, etc.)

## Documentation

- [SDK Overview](../README.md) - Full SDK documentation
- [API Reference](../docs/api-reference.md) - Detailed API docs
- [Testing Guide](../docs/testing.md) - Testing strategies
- [Best Practices](../docs/best-practices.md) - Development guidelines

## Getting Help

- GitHub Issues: [nadoo-ai-kb/issues](https://github.com/nadoo/nadoo-ai-kb/issues)
- Documentation: [docs.nadoo.ai](https://docs.nadoo.ai)
- Email: support@nadoo.ai

## Contributing

Want to contribute an example? Please:

1. Follow the existing structure
2. Include comprehensive tests
3. Write clear documentation
4. Submit a pull request

## License

MIT License - see main SDK documentation for details.
