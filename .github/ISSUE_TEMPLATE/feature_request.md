---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description
A clear and concise description of the feature you'd like to see.

## Use Case
Describe the use case or problem this feature would solve.

**Example:**
"As a plugin developer, I want to [do something] so that [benefit]."

## Proposed Solution
Describe how you envision this feature working.

**Example API:**
```python
from nadoo_plugin import NadooPlugin, new_decorator

class MyPlugin(NadooPlugin):
    @new_decorator(option="value")
    def my_tool(self) -> dict:
        # ...
```

## Alternatives Considered
Have you considered any alternative solutions or workarounds?

## Additional Context
- Is this breaking existing functionality?
- Would this require changes to the manifest format?
- Are there any security implications?

## Benefits
- Who would benefit from this feature?
- How common is this use case?

## Related Issues
Link any related issues or discussions.
