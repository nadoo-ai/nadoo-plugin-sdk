"""
Create command - Generate new plugin project
"""

import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


PLUGIN_TEMPLATE = '''from nadoo_plugin import NadooPlugin, tool, parameter


class {class_name}(NadooPlugin):
    """
    {description}
    """

    def on_initialize(self):
        """Initialize plugin - load config, check env vars, etc."""
        self.context.log("Plugin initialized")

    @tool(
        name="example_tool",
        description="An example tool that processes text"
    )
    @parameter("text", type="string", required=True, description="Text to process")
    @parameter("mode", type="string", required=False, default="upper", description="Processing mode")
    def example_tool(self, text: str, mode: str = "upper") -> dict:
        """
        Example tool implementation

        Args:
            text: Input text
            mode: Processing mode (upper, lower, reverse)

        Returns:
            Result dictionary
        """
        self.context.log(f"Processing text in {{mode}} mode")
        self.context.watch_variable("input_length", len(text))

        if mode == "upper":
            result = text.upper()
        elif mode == "lower":
            result = text.lower()
        elif mode == "reverse":
            result = text[::-1]
        else:
            result = text

        return {{
            "result": result,
            "mode": mode,
            "length": len(result)
        }}
'''


MANIFEST_TEMPLATE = '''name: {name}
display_name: {display_name}
version: 0.1.0
author: {author}
description: {description}

# SDK version requirement
sdk_version: ">=0.1.0"

# Entry point
entry_point: main.py
python_version: ">=3.9"

# Permissions
permissions:
  - llm_access
  - storage

# Environment variables
environment_variables:
  - name: API_KEY
    required: false
    description: Optional API key for external service

# Tools
tools:
  - name: example_tool
    description: An example tool that processes text
    parameters:
      - name: text
        type: string
        required: true
        description: Text to process
      - name: mode
        type: string
        required: false
        default: upper
        description: Processing mode (upper, lower, reverse)

# Resource limits
resource_limits:
  memory_mb: 100
  timeout_seconds: 30

# Metadata
homepage: https://github.com/your-username/{name}
repository: https://github.com/your-username/{name}
license: MIT
keywords:
  - text
  - processing
'''


README_TEMPLATE = '''# {display_name}

{description}

## Installation

```bash
nadoo-plugin install {name}-0.1.0.nadoo-plugin --workspace <workspace-id>
```

## Development

### Test locally
```bash
nadoo-plugin test --tool example_tool --params '{{"text": "Hello World"}}'
```

### Build package
```bash
nadoo-plugin build
```

## Tools

### example_tool

Process text using various modes.

**Parameters:**
- `text` (string, required): Text to process
- `mode` (string, optional): Processing mode (upper, lower, reverse)

**Example:**
```python
result = plugin.example_tool(text="Hello World", mode="upper")
# Returns: {{"result": "HELLO WORLD", "mode": "upper", "length": 11}}
```

## License

MIT
'''


GITIGNORE_TEMPLATE = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Plugin build
*.nadoo-plugin

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
'''


REQUIREMENTS_TEMPLATE = '''nadoo-plugin-sdk>=0.1.0
'''


def create_plugin(name: str, author: str, description: str):
    """Create new plugin project"""

    # Validate name
    if not name.replace('-', '').replace('_', '').isalnum():
        console.print("[red]Error: Plugin name must contain only letters, numbers, hyphens, and underscores[/red]")
        return

    # Create project directory
    project_dir = Path(name)
    if project_dir.exists():
        console.print(f"[red]Error: Directory '{name}' already exists[/red]")
        return

    try:
        project_dir.mkdir(parents=True)

        # Generate class name
        class_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))

        # Set defaults
        if not author:
            author = "Plugin Developer"
        if not description:
            description = f"A Nadoo plugin for {name}"

        display_name = ' '.join(word.capitalize() for word in name.replace('-', ' ').replace('_', ' ').split())

        # Create files
        files = {
            'main.py': PLUGIN_TEMPLATE.format(
                class_name=class_name,
                description=description
            ),
            'manifest.yaml': MANIFEST_TEMPLATE.format(
                name=name,
                display_name=display_name,
                author=author,
                description=description
            ),
            'README.md': README_TEMPLATE.format(
                display_name=display_name,
                description=description,
                name=name
            ),
            '.gitignore': GITIGNORE_TEMPLATE,
            'requirements.txt': REQUIREMENTS_TEMPLATE,
        }

        for filename, content in files.items():
            file_path = project_dir / filename
            file_path.write_text(content.strip() + '\n')

        # Success message
        console.print()
        console.print(Panel.fit(
            f"[green]✓[/green] Plugin project created: [bold]{name}[/bold]\n\n"
            f"Next steps:\n"
            f"  1. cd {name}\n"
            f"  2. Edit main.py to implement your plugin\n"
            f"  3. Update manifest.yaml with your plugin details\n"
            f"  4. Test: nadoo-plugin test --tool example_tool --params '{json_example}'\n"
            f"  5. Build: nadoo-plugin build",
            title="Success",
            border_style="green"
        ))
        console.print()

    except Exception as e:
        console.print(f"[red]Error creating plugin: {str(e)}[/red]")
        # Cleanup on error
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)


# Example JSON for test command
json_example = '{"text": "Hello"}'
