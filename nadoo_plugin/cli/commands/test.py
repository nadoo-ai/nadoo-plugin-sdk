"""
Test command - Test plugin locally
"""

import json
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()


def test_plugin(tool_name: str, params_json: str, debug: bool) -> int:
    """Test plugin tool locally

    Returns:
        0 if test passed, 1 if failed
    """

    # Check manifest
    if not Path('manifest.yaml').exists():
        console.print("[red]Error: manifest.yaml not found[/red]")
        return 1

    try:
        import yaml
        with open('manifest.yaml', 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)

        # Parse parameters
        try:
            params = json.loads(params_json)
        except json.JSONDecodeError as e:
            console.print(f"[red]Error parsing parameters JSON: {str(e)}[/red]")
            return

        # Load plugin module
        entry_point = Path(manifest['entry_point'])
        if not entry_point.exists():
            console.print(f"[red]Error: Entry point '{entry_point}' not found[/red]")
            return

        # Add current directory to Python path
        sys.path.insert(0, str(Path.cwd()))

        # Import plugin SDK
        try:
            from nadoo_plugin import NadooPlugin, PluginContext
            from nadoo_plugin.api import InternalAPIClient
        except ImportError:
            console.print("[red]Error: nadoo-plugin-sdk not installed[/red]")
            console.print("Install it with: pip install nadoo-plugin-sdk")
            return

        # Import plugin module
        import importlib.util
        spec = importlib.util.spec_from_file_location("plugin_module", entry_point)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find plugin class
        plugin_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr_name != 'NadooPlugin':
                if issubclass(attr, NadooPlugin) and attr != NadooPlugin:
                    plugin_class = attr
                    break

        if not plugin_class:
            console.print("[red]Error: No NadooPlugin subclass found[/red]")
            return

        # Create mock context
        from nadoo_plugin.testing.mocks import MockContext, MockAPIClient

        context = MockContext(
            execution_id="test-execution",
            plugin_id="test-plugin",
            workspace_id="test-workspace",
            permissions=manifest.get('permissions', []),
            debug_mode=debug
        )

        # Create mock API client
        api = MockAPIClient(context)

        # Initialize plugin
        console.print(f"[blue]Testing plugin: {manifest['display_name']}[/blue]")
        console.print(f"[blue]Tool: {tool_name}[/blue]")
        console.print()

        plugin = plugin_class()
        plugin.initialize(context, api)

        # Execute tool
        console.print("[yellow]Executing...[/yellow]")
        result = plugin.execute(tool_name, params)

        # Display result
        console.print()
        console.print("[green]✓ Execution successful[/green]")
        console.print()
        console.print("[bold]Result:[/bold]")
        console.print(json.dumps(result, indent=2))

        # Display debug info if enabled
        if debug:
            console.print()
            console.print("[bold]Debug Information:[/bold]")

            # Logs
            logs = context.get_logs()
            if logs:
                console.print()
                console.print("[bold]Logs:[/bold]")
                for log in logs:
                    console.print(f"  [{log['level'].upper()}] {log['message']}")

            # Steps
            steps = context.get_steps()
            if steps:
                console.print()
                console.print("[bold]Steps:[/bold]")
                table = Table(show_header=True)
                table.add_column("Step")
                table.add_column("Duration")
                for step in steps:
                    duration = f"{step['duration']:.3f}s" if step.get('duration') else "-"
                    table.add_row(step['step_name'], duration)
                console.print(table)

            # Trace events
            trace = context.get_trace()
            if trace:
                console.print()
                console.print("[bold]Trace Events:[/bold]")
                for event in trace[:10]:  # Show first 10 events
                    console.print(f"  [{event['execution_time']:.3f}s] {event['event']}")
                if len(trace) > 10:
                    console.print(f"  ... and {len(trace) - 10} more events")

            # Variables
            variables = context.get_variables()
            if variables:
                console.print()
                console.print("[bold]Variables:[/bold]")
                for name, value in variables.items():
                    console.print(f"  {name} = {value}")

        # Finalize
        plugin.finalize()
        api.close()

        return 0  # Success

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if debug:
            import traceback
            console.print()
            console.print(traceback.format_exc())
        return 1  # Failure
