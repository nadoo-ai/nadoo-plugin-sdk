---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Execute command '...'
3. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
What actually happened.

## Code Example
```python
# Minimal code to reproduce the issue
from nadoo_plugin import NadooPlugin, tool

class MyPlugin(NadooPlugin):
    @tool(name="test_tool", description="Test")
    def test_tool(self) -> dict:
        # ...
```

## Error Message
```
Paste the full error message here
```

## Environment
- **OS**: [e.g., macOS 13.0, Ubuntu 22.04, Windows 11]
- **Python Version**: [e.g., 3.11.5]
- **nadoo-plugin-sdk Version**: [e.g., 0.1.0]
- **Installation Method**: [pip, poetry, etc.]

## Additional Context
Add any other context about the problem here.

## Possible Solution
(Optional) If you have ideas on how to fix this, please share.
