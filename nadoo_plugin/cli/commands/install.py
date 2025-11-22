"""
Install command - Install plugin to workspace via API
"""

import httpx
from pathlib import Path
from rich.console import Console

console = Console()


def install_plugin(package_file: str, workspace: str, api_url: str, api_key: str):
    """Install plugin to workspace"""

    package_path = Path(package_file)
    if not package_path.exists():
        console.print(f"[red]Error: Package file '{package_file}' not found[/red]")
        return

    if not api_key:
        console.print("[red]Error: API key is required[/red]")
        console.print("Provide it with --api-key option")
        return

    try:
        console.print(f"[blue]Uploading plugin to workspace {workspace}...[/blue]")

        # Upload plugin
        with open(package_path, 'rb') as f:
            files = {'file': (package_path.name, f, 'application/octet-stream')}
            headers = {'Authorization': f'Bearer {api_key}'}

            response = httpx.post(
                f"{api_url}/api/v1/workspaces/{workspace}/plugins/upload",
                files=files,
                headers=headers,
                timeout=60.0
            )

        if response.status_code != 200:
            console.print(f"[red]Error: Upload failed[/red]")
            console.print(f"Status: {response.status_code}")
            console.print(f"Response: {response.text}")
            return

        plugin_data = response.json()
        plugin_id = plugin_data.get('id')
        plugin_name = plugin_data.get('display_name')

        console.print(f"[green]✓ Plugin uploaded successfully[/green]")
        console.print(f"  Plugin: {plugin_name}")
        console.print(f"  ID: {plugin_id}")
        console.print()
        console.print("[yellow]Next step: Install the plugin via web UI[/yellow]")
        console.print(f"  URL: {api_url.replace('/api', '')}/plugin/{plugin_id}")

    except httpx.RequestError as e:
        console.print(f"[red]Error: Network request failed: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
