"""
Nadoo Plugin CLI - Main entry point
"""

import sys
import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="nadoo-plugin")
def cli():
    """Nadoo Plugin SDK CLI - Tools for developing Nadoo plugins"""
    pass


@cli.command()
@click.argument('name')
@click.option('--author', default='', help='Plugin author name')
@click.option('--description', default='', help='Plugin description')
def create(name: str, author: str, description: str):
    """Create a new plugin project"""
    from .commands.create import create_plugin
    create_plugin(name, author, description)


@cli.command()
@click.option('--manifest', default='manifest.yaml', help='Path to manifest.yaml')
def validate(manifest: str):
    """Validate plugin manifest and code"""
    from .commands.validate import validate_plugin
    exit_code = validate_plugin(manifest)
    sys.exit(exit_code)


@cli.command()
@click.option('--tool', required=True, help='Tool name to test')
@click.option('--params', default='{}', help='JSON parameters')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def test(tool: str, params: str, debug: bool):
    """Test plugin tool locally"""
    from .commands.test import test_plugin
    exit_code = test_plugin(tool, params, debug)
    sys.exit(exit_code)


@cli.command()
@click.option('--output', default=None, help='Output file name')
def build(output: str):
    """Build .nadoo-plugin package"""
    from .commands.build import build_plugin
    build_plugin(output)


@cli.command()
@click.argument('package_file')
@click.option('--workspace', required=True, help='Workspace ID')
@click.option('--api-url', default='http://localhost:8000', help='Nadoo API URL')
@click.option('--api-key', help='API key for authentication')
def install(package_file: str, workspace: str, api_url: str, api_key: str):
    """Install plugin to workspace"""
    from .commands.install import install_plugin
    install_plugin(package_file, workspace, api_url, api_key)


if __name__ == '__main__':
    cli()
