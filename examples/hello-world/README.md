# Hello World Plugin

A simple example plugin demonstrating the basic features of the Nadoo Plugin SDK.

## Features

This plugin demonstrates:

- **Basic tool definition** with `@tool` decorator
- **Parameter validation** with `@parameter` and `@validator` decorators
- **Context usage** for logging and debugging
- **Multiple tools** in a single plugin
- **Error handling** and validation

## Tools

### 1. greet

Generate a greeting message in multiple languages.

**Parameters:**
- `name` (string, required): Name of the person to greet
- `language` (string, optional): Language for greeting (english, spanish, french, korean)

**Example:**
```json
{
  "name": "Alice",
  "language": "spanish"
}
```

**Response:**
```json
{
  "success": true,
  "greeting": "¡Hola, Alice! ¡Bienvenido a Nadoo!",
  "language": "spanish",
  "name": "Alice"
}
```

### 2. echo

Echo back text with optional transformations.

**Parameters:**
- `text` (string, required): Text to echo (1-1000 characters)
- `transform` (string, optional): Transformation to apply (none, uppercase, lowercase, reverse)

**Example:**
```json
{
  "text": "Hello World",
  "transform": "uppercase"
}
```

**Response:**
```json
{
  "success": true,
  "original": "Hello World",
  "result": "HELLO WORLD",
  "transform": "uppercase"
}
```

### 3. add_numbers

Add two numbers together.

**Parameters:**
- `a` (number, required): First number
- `b` (number, required): Second number

**Example:**
```json
{
  "a": 5,
  "b": 3
}
```

**Response:**
```json
{
  "success": true,
  "a": 5,
  "b": 3,
  "sum": 8
}
```

## Installation

1. Install the Nadoo CLI:
```bash
pip install nadoo-cli
```

2. Install the plugin:
```bash
nadoo plugin install hello-world
```

3. Use the plugin in your workspace:
```bash
nadoo plugin enable hello-world
```

## Development

### Running Tests

```bash
cd examples/hello-world
python -m pytest test_hello_world.py -v
```

Or using unittest:

```bash
python test_hello_world.py
```

### Code Structure

```
hello-world/
├── main.py              # Plugin implementation
├── manifest.yaml        # Plugin metadata and configuration
├── test_hello_world.py  # Unit tests
└── README.md           # This file
```

### Key Concepts

#### Plugin Class

All plugins inherit from `NadooPlugin`:

```python
from nadoo_plugin import NadooPlugin, tool, parameter, validator

class HelloWorldPlugin(NadooPlugin):
    """Hello World plugin demonstrating basic features"""

    def on_initialize(self):
        """Called when plugin is loaded"""
        self.context.info("Hello World plugin initialized")

    @tool(name="greet", description="Generate a greeting message")
    @parameter("name", type="string", required=True, description="Name to greet")
    def greet(self, name: str) -> dict:
        return {"success": True, "greeting": f"Hello, {name}!"}
```

#### Tool Definition

```python
@tool(name="greet", description="Generate a greeting message")
@parameter("name", type="string", required=True, description="Name to greet")
def greet(self, name: str) -> dict:
    return {"success": True, "greeting": f"Hello, {name}!"}
```

#### Parameter Validation

```python
@validator("language", allowed_values=["english", "spanish", "french", "korean"])
def greet(self, name: str, language: str = "english") -> dict:
    # Language will be validated before this executes
    pass
```

#### Context Usage

```python
# Logging
self.context.info("Processing request")
self.context.warn("Something unusual happened")
self.context.error("Error occurred")

# Tracing
self.context.trace("event_name", {"key": "value"})

# Variable watching
self.context.watch_variable("result", result_value)
```

## Learning Path

This plugin is designed as a learning tool. Here's what each part teaches:

1. **greet tool**: Basic tool structure, parameter handling, and multi-language support
2. **echo tool**: Parameter validation, text transformation, and variable watching
3. **add_numbers tool**: Numeric parameters and simple calculations
4. **test_hello_world.py**: Comprehensive testing patterns using PluginTestCase

## Next Steps

After understanding this example, check out:

- **llm-summarizer**: Learn how to use the LLM API
- **Documentation**: Read the full SDK documentation at `/packages/nadoo-plugin-sdk/README.md`
- **Create your own**: Use `nadoo plugin create` to start your own plugin

## License

MIT License - see main SDK documentation for details.
