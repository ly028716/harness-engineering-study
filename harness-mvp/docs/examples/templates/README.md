# Custom Templates

This directory contains custom task templates for Harness MVP.

## Quick Start

1. Create a JSON file with your template definition
2. Save it in this directory (`.harness/templates/`)
3. Use it with `harness plan add --template <name>`

## Template Format

```json
{
  "name": "template-name",
  "title": "Task Title {variable_name}",
  "description": "Task description\ncan contain {variables}",
  "priority": "REQUIRED|RECOMMENDED|OPTIONAL",
  "estimated_effort": 1-5,
  "acceptance_criteria": [
    "Criterion 1",
    "Criterion 2"
  ],
  "prompts": [
    {
      "key": "variable_name",
      "question": "Question to ask user",
      "required": true,
      "multiline": false,
      "default": "Optional default value"
    }
  ]
}
```

## Field Reference

### Required Fields
- `name` - Template identifier (letters, numbers, underscore, hyphen only)
- `title` - Task title (can include `{variable}` placeholders)
- `description` - Task description (can include `{variable}` placeholders)
- `priority` - One of: REQUIRED, RECOMMENDED, OPTIONAL
- `estimated_effort` - Integer 1-5
- `prompts` - Array of prompt objects (at least one required)

### Prompt Fields
- `key` (required) - Variable name (valid Python identifier)
- `question` (required) - Question to ask user
- `required` (optional) - Whether input is mandatory (default: true)
- `multiline` (optional) - Whether to accept multi-line input (default: false)
- `default` (optional) - Default value for optional fields

## Example: Documentation Template

See `documentation.json` in this directory for a complete working example.

```bash
# List all templates (including custom)
harness template list

# View template details
harness template show documentation

# Use the template
harness plan add --template documentation
```

## Validation Rules

Your template must pass these checks:

1. `name` must be a valid identifier
2. `priority` must be REQUIRED, RECOMMENDED, or OPTIONAL
3. `estimated_effort` must be 1-5
4. All `{variables}` in title/description must be defined in `prompts`
5. Each `prompt.key` must be a valid Python identifier
6. No duplicate prompt keys

## Tips

- Use descriptive variable names like `feature_name`, not `x` or `var1`
- Set `multiline: true` for long text inputs (descriptions, steps, etc.)
- Use `default` values for optional fields to improve UX
- Keep templates focused - one template per task type
- Use Markdown formatting in `description` for better readability

## Getting Help

For more information, see:
- Main README: `../../README.md`
- API Reference: `../../../docs/api-reference.md`
- Template Requirements: `../.kiro/specs/task-template-system/requirements.md`
