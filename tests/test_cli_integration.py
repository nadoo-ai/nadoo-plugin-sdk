"""
Integration tests for CLI commands

Tests actual CLI execution with real plugins to catch issues like:
- Data structure mismatches
- Missing fields in context
- Incorrect API usage
"""
import os
import json
import subprocess
import tempfile
from pathlib import Path
import pytest


class TestCLIIntegration:
    """Integration tests for all CLI commands"""

    @pytest.fixture
    def hello_world_plugin(self):
        """Path to hello-world example plugin"""
        sdk_root = Path(__file__).parent.parent
        plugin_dir = sdk_root / "examples" / "hello-world"
        assert plugin_dir.exists(), f"hello-world plugin not found at {plugin_dir}"
        return plugin_dir

    def test_validate_command(self, hello_world_plugin):
        """Test nadoo-plugin validate command"""
        result = subprocess.run(
            ["nadoo-plugin", "validate"],
            cwd=hello_world_plugin,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Validate failed: {result.stderr}"
        assert "validation passed" in result.stdout.lower()

    def test_test_command_basic(self, hello_world_plugin):
        """Test nadoo-plugin test command without debug"""
        result = subprocess.run(
            [
                "nadoo-plugin", "test",
                "--tool", "greet",
                "--params", '{"name": "TestUser", "language": "english"}'
            ],
            cwd=hello_world_plugin,
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, f"Test failed: {result.stderr}"
        assert "successful" in result.stdout.lower()
        assert "TestUser" in result.stdout

    def test_test_command_with_debug(self, hello_world_plugin):
        """Test nadoo-plugin test command with debug mode

        This test specifically checks that debug mode doesn't crash
        due to data structure issues (like the step_name KeyError bug)
        """
        result = subprocess.run(
            [
                "nadoo-plugin", "test",
                "--tool", "greet",
                "--params", '{"name": "Alice", "language": "korean"}',
                "--debug"
            ],
            cwd=hello_world_plugin,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should not crash
        assert result.returncode == 0, f"Test with debug failed: {result.stderr}"

        # Should show debug information
        assert "Logs:" in result.stdout or "logs:" in result.stdout.lower()
        assert "Steps:" in result.stdout or "steps:" in result.stdout.lower()

        # Should not have KeyError or similar errors
        assert "KeyError" not in result.stderr
        assert "Traceback" not in result.stderr or "Tool executed successfully" in result.stdout

    def test_test_command_all_tools(self, hello_world_plugin):
        """Test all tools in hello-world plugin"""
        tools = [
            ("greet", '{"name": "Bob", "language": "spanish"}'),
            ("echo", '{"text": "Hello World", "transform": "uppercase"}'),
            ("add_numbers", '{"a": 5, "b": 3}')
        ]

        for tool_name, params in tools:
            result = subprocess.run(
                [
                    "nadoo-plugin", "test",
                    "--tool", tool_name,
                    "--params", params
                ],
                cwd=hello_world_plugin,
                capture_output=True,
                text=True,
                timeout=10
            )

            assert result.returncode == 0, \
                f"Tool {tool_name} failed: {result.stderr}"
            assert "successful" in result.stdout.lower()

    def test_build_command(self, hello_world_plugin):
        """Test nadoo-plugin build command"""
        # Clean up any existing builds
        for f in hello_world_plugin.glob("*.nadoo-plugin"):
            f.unlink()

        result = subprocess.run(
            ["nadoo-plugin", "build"],
            cwd=hello_world_plugin,
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, f"Build failed: {result.stderr}"
        assert "built successfully" in result.stdout.lower()

        # Check that .nadoo-plugin file was created
        plugin_files = list(hello_world_plugin.glob("*.nadoo-plugin"))
        assert len(plugin_files) == 1, f"Expected 1 plugin file, found {len(plugin_files)}"
        assert plugin_files[0].exists()

    def test_invalid_manifest(self):
        """Test that validation catches invalid manifest"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create invalid manifest (missing required fields)
            manifest = tmpdir / "manifest.yaml"
            manifest.write_text("""
name: test-plugin
# Missing version and other required fields
""")

            result = subprocess.run(
                ["nadoo-plugin", "validate"],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )

            # Should fail validation
            assert result.returncode != 0
            output = (result.stdout + result.stderr).lower()
            assert "missing" in output or "required" in output

    def test_parameter_validation_error(self, hello_world_plugin):
        """Test that parameter validation errors are handled gracefully"""
        # Test with invalid language (not in allowed values)
        result = subprocess.run(
            [
                "nadoo-plugin", "test",
                "--tool", "greet",
                "--params", '{"name": "Test", "language": "invalid_language"}'
            ],
            cwd=hello_world_plugin,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should fail gracefully
        assert result.returncode != 0
        # Error message should be informative
        output = (result.stdout + result.stderr).lower()
        assert "language" in output or "validation" in output

    def test_missing_parameter_error(self, hello_world_plugin):
        """Test that missing required parameters are caught"""
        # Test without required 'name' parameter
        result = subprocess.run(
            [
                "nadoo-plugin", "test",
                "--tool", "greet",
                "--params", '{}'
            ],
            cwd=hello_world_plugin,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should fail gracefully
        assert result.returncode != 0
        output = (result.stdout + result.stderr).lower()
        assert "name" in output or "required" in output

    def test_debug_data_structure_integrity(self, hello_world_plugin):
        """Test that debug data structures are consistent

        This catches issues like:
        - Missing keys in step dictionaries
        - Wrong field names
        - Type mismatches
        """
        result = subprocess.run(
            [
                "nadoo-plugin", "test",
                "--tool", "greet",
                "--params", '{"name": "StructureTest"}',
                "--debug"
            ],
            cwd=hello_world_plugin,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should complete successfully
        assert result.returncode == 0, f"Failed: {result.stderr}"

        # Debug output should contain expected sections
        output_lower = result.stdout.lower()
        assert "logs:" in output_lower
        assert "steps:" in output_lower
        assert "trace" in output_lower

        # Should not have any Python errors
        assert "error:" not in output_lower or "executed successfully" in output_lower
        assert "traceback" not in output_lower or "executed successfully" in output_lower
        assert "keyerror" not in output_lower
        assert "attributeerror" not in output_lower


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
