"""
Build command - Build .nadoo-plugin package
"""

import os
import zipfile
import yaml
from pathlib import Path
from rich.console import Console

console = Console()


def build_plugin(output: str = None):
    """Build plugin package"""

    # Check manifest exists
    if not Path('manifest.yaml').exists():
        console.print("[red]Error: manifest.yaml not found in current directory[/red]")
        return

    try:
        # Load manifest
        with open('manifest.yaml', 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)

        name = manifest['name']
        version = manifest['version']

        # Determine output filename
        if not output:
            output = f"{name}-{version}.nadoo-plugin"

        # Create zip file
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add manifest
            zipf.write('manifest.yaml')

            # Add entry point
            entry_point = manifest['entry_point']
            if not Path(entry_point).exists():
                console.print(f"[red]Error: Entry point '{entry_point}' not found[/red]")
                return
            zipf.write(entry_point)

            # Add other Python files in current directory
            for file in Path('.').glob('*.py'):
                if file.name != entry_point:
                    zipf.write(file)

            # Add README if exists
            if Path('README.md').exists():
                zipf.write('README.md')

            # Add requirements.txt if exists
            if Path('requirements.txt').exists():
                zipf.write('requirements.txt')

        file_size = Path(output).stat().st_size / 1024  # KB

        console.print(f"[green]✓ Plugin package built successfully[/green]")
        console.print(f"  Output: {output}")
        console.print(f"  Size: {file_size:.2f} KB")
        console.print()
        console.print("Next steps:")
        console.print(f"  1. Upload to Nadoo workspace")
        console.print(f"  2. Or install via CLI: nadoo-plugin install {output} --workspace <workspace-id>")

    except Exception as e:
        console.print(f"[red]Error building plugin: {str(e)}[/red]")
        if Path(output).exists():
            Path(output).unlink()
