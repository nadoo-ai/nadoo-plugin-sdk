# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Plugin marketplace integration
- Hot-reload support for development
- Plugin dependency management
- Advanced debugging features
- Performance profiling tools
- Plugin templates gallery

## [0.1.0] - 2025-11-22

### Added
- Initial public release
- Core plugin SDK framework
- `NadooPlugin` base class for plugin development
- Decorator support for defining tools
  - `@tool` - Define plugin tools
  - `@parameter` - Define tool parameters
  - `@validator` - Add custom validation
  - `@permission_required` - Require specific permissions
- Plugin context API
  - `context.log()` - Logging
  - `context.get_env()` - Environment variables
  - `context.require_env()` - Required environment variables
- Internal API access
  - `api.llm` - LLM service integration
  - `api.tools` - Tool invocation
  - `api.knowledge` - Knowledge base access
  - `api.storage` - Storage service
- CLI tooling
  - `nadoo-plugin create` - Create new plugin
  - `nadoo-plugin build` - Build plugin package
  - `nadoo-plugin test` - Test plugin tools
  - `nadoo-plugin install` - Install plugin to workspace
- Testing utilities
  - `PluginTestCase` base class
  - Mock services for testing
  - Test helpers and fixtures
- Real-time debugging
  - WebSocket-based debug inspector
  - Live execution metrics
  - Performance tracking
- Workflow integration
  - Seamless integration with Nadoo workflows
  - Variable passing support
  - Error handling and propagation
- Type safety
  - Full type hints throughout
  - Runtime validation with Pydantic
  - IDE autocomplete support
- Documentation
  - Comprehensive README
  - API reference
  - Example plugins (hello-world, llm-summarizer)
  - CLI usage guide

### Features
- **Simple API**: Clean, intuitive interface
- **Type Safe**: Full type hints and validation
- **Rich Tooling**: CLI for plugin lifecycle
- **Well Documented**: Examples and guides
- **Testing Support**: Built-in test utilities
- **Decorator Support**: Clean, readable code
- **Real-time Debugging**: WebSocket inspector
- **Internal APIs**: LLM, Tools, KB, Storage
- **Workflow Integration**: First-class support
- **Performance Tracking**: Built-in metrics

### Development
- Poetry-based build system
- Black code formatting (line-length: 120)
- isort import sorting
- Flake8 linting
- mypy type checking
- pytest testing framework
- pytest-asyncio for async tests
- pytest-cov for coverage

### Dependencies
- `pydantic` ^2.5.0 - Type validation
- `httpx` ^0.25.0 - HTTP client
- `pyyaml` ^6.0 - YAML parsing
- `click` ^8.1.0 - CLI framework
- `rich` ^13.7.0 - Terminal formatting

### Examples
- `hello-world` - Basic plugin example
- `llm-summarizer` - LLM integration example

## [0.0.1] - 2024-11-XX (Internal)

### Added
- Initial internal prototype
- Basic plugin loading
- Simple tool registration
- Proof of concept

---

## Version Naming Convention

- **Major (X.0.0)**: Breaking API changes
- **Minor (0.X.0)**: New features, backward compatible
- **Patch (0.0.X)**: Bug fixes, backward compatible

## Release Process

1. Update CHANGELOG.md with version and date
2. Update version in pyproject.toml
3. Run full test suite: `poetry run pytest`
4. Run code quality checks:
   ```bash
   poetry run black --check .
   poetry run isort --check-only .
   poetry run flake8 nadoo_plugin tests
   poetry run mypy nadoo_plugin
   ```
5. Build package: `poetry build`
6. Create git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
7. Push tag: `git push origin vX.Y.Z`
8. Upload to PyPI: `poetry publish`
9. Create GitHub Release

---

[Unreleased]: https://github.com/nadoo-ai/nadoo-plugin-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/nadoo-ai/nadoo-plugin-sdk/releases/tag/v0.1.0
[0.0.1]: https://github.com/nadoo-ai/nadoo-plugin-sdk/releases/tag/v0.0.1
