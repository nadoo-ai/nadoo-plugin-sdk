## Description
<!-- Provide a clear and concise description of what this PR does -->

Fixes # (issue)

## Type of Change
<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code quality improvement (refactoring, type hints, etc.)
- [ ] New decorator
- [ ] CLI improvement
- [ ] Testing improvement

## Changes Made
<!-- List the specific changes made in this PR -->

-
-
-

## Testing
<!-- Describe the tests you ran to verify your changes -->

### Test commands run:
```bash
poetry run pytest
poetry run black --check .
poetry run isort --check-only .
poetry run flake8 nadoo_plugin tests
poetry run mypy nadoo_plugin
```

### Manual testing:
<!-- Describe any manual testing you performed -->

-

## Documentation
<!-- Have you updated the relevant documentation? -->

- [ ] Updated README.md (if applicable)
- [ ] Updated CHANGELOG.md
- [ ] Added/updated docstrings
- [ ] Updated examples (if applicable)

## Checklist
<!-- Mark completed items with an "x" -->

- [ ] My code follows the code style of this project (Black, isort)
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] All code quality checks pass (Black, isort, Flake8, mypy)
- [ ] I have updated the documentation accordingly
- [ ] My changes generate no new warnings
- [ ] I have checked that my changes don't introduce security vulnerabilities

## Breaking Changes
<!-- If this is a breaking change, describe what breaks and migration path -->

**What breaks:**
-

**Migration guide:**
```python
# Before
old_code()

# After
new_code()
```

## Screenshots / Examples
<!-- If applicable, add screenshots or code examples to help explain your changes -->

```python
# Example usage of new feature
```

## Additional Notes
<!-- Add any other context about the PR here -->
