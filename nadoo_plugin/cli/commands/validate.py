"""
Validate command - Validate plugin manifest and code
"""

import yaml
from pathlib import Path
from rich.console import Console
from pydantic import ValidationError

console = Console()


def validate_plugin(manifest_path: str) -> int:
    """Validate plugin

    Returns:
        0 if validation passed, 1 if failed
    """
    manifest_file = Path(manifest_path)

    if not manifest_file.exists():
        console.print(f"[red]Error: {manifest_path} not found[/red]")
        return 1

    try:
        # Load manifest
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest_data = yaml.safe_load(f)

        # Validate with Pydantic (import from parent package)
        from nadoo_plugin.api.client import BaseAPIClient
        # Note: In production, import PluginManifest schema
        # For now, basic validation

        # Check required fields
        required_fields = ['name', 'display_name', 'version', 'author', 'description',
                          'sdk_version', 'entry_point', 'tools']

        missing = [f for f in required_fields if f not in manifest_data]
        if missing:
            console.print(f"[red]Error: Missing required fields: {', '.join(missing)}[/red]")
            return 1

        # Check entry point exists
        entry_point = Path(manifest_data['entry_point'])
        if not entry_point.exists():
            console.print(f"[red]Error: Entry point '{entry_point}' not found[/red]")
            return 1

        # Check version format
        version = manifest_data['version']
        if not version.count('.') == 2:
            console.print(f"[red]Error: Version must be in format X.Y.Z (e.g., 0.1.0)[/red]")
            return 1

        console.print("[green]✓ Manifest validation passed[/green]")
        console.print(f"  Plugin: {manifest_data['display_name']} v{manifest_data['version']}")
        console.print(f"  Tools: {len(manifest_data.get('tools', []))}")
        console.print(f"  Permissions: {len(manifest_data.get('permissions', []))}")
        return 0

    except yaml.YAMLError as e:
        console.print(f"[red]Error parsing YAML: {str(e)}[/red]")
        return 1
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return 1
