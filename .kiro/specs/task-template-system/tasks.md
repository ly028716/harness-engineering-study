# Implementation Plan: Task Template System

## Overview

This implementation plan converts the Task Template System design into actionable coding tasks. The system will enable rapid creation of standardized tasks through templates with variable replacement, supporting both built-in and custom user templates.

**Implementation Language**: Python 3.8+

**Key Components**:
- Template data models (TemplatePrompt, TaskTemplate)
- Template storage and loading (TemplateStore)
- Template engine with variable replacement (TemplateEngine)
- CLI command integration for template operations

## Tasks

- [x] 1. Create core template data models and validation
  - [x] 1.1 Implement TemplatePrompt dataclass in `harness/templates.py`
    - Create TemplatePrompt with fields: key, question, required, multiline, default
    - Implement validate() method to check key format and required fields
    - _Requirements: 3.1, 3.5.2_
  
  - [x] 1.2 Implement TaskTemplate dataclass in `harness/templates.py`
    - Create TaskTemplate with fields: name, title, description, priority, estimated_effort, prompts, acceptance_criteria
    - Implement get_variables() method to extract {variable} placeholders using regex pattern `\{([a-zA-Z_][a-zA-Z0-9_]*)\}`
    - Implement to_dict() and from_dict() serialization methods
    - _Requirements: 3.1, 3.2, 3.5.1_
  
  - [x] 1.3 Write property test for variable extraction completeness
    - **Property 1: Variable Extraction Completeness**
    - **Validates: Requirements 3.2.1**
    - Test that get_variables() extracts all valid {variable} patterns
    - Use Hypothesis to generate template strings with various variable patterns
  
  - [x] 1.4 Implement TaskTemplate validate() method
    - Check name matches pattern `^[a-zA-Z0-9_-]+$`
    - Validate priority is valid Priority enum value
    - Validate estimated_effort is in range [1,5]
    - Validate prompts list is non-empty
    - Check variable-prompt consistency (all template variables defined in prompts)
    - Return list of error strings
    - _Requirements: 3.5.1, 3.5.2, 3.5.3_
  
  - [x] 1.5 Write property test for template name validation
    - **Property 5: Template Name Validation**
    - **Validates: Requirements 3.5.1**
    - Test that validation accepts valid names and rejects invalid ones
  
  - [x] 1.6 Write property test for serialization round-trip
    - **Property 4: Template Serialization Round-Trip**
    - **Validates: Requirements 3.2.4**
    - Test that to_dict() → from_dict() preserves template equivalence

- [x] 2. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Implement built-in templates and template store
  - [x] 3.1 Create TemplateStore class in `harness/template_loader.py`
    - Initialize with harness_dir path
    - Set custom_template_dir to harness_dir / "templates"
    - Implement _load_built_in_templates() with feature, bugfix, refactor templates as specified in requirements 3.1.1-3.1.3
    - _Requirements: 3.1_
  
  - [x] 3.2 Implement custom template loading in TemplateStore
    - Implement load_custom_templates() to read .json files from .harness/templates/
    - Parse JSON and create TaskTemplate via from_dict()
    - Validate loaded templates and log warnings for invalid ones
    - Handle JSON parse errors gracefully
    - _Requirements: 3.4_
  
  - [x] 3.3 Write property test for custom template loading preservation
    - **Property 8: Custom Template Loading Preservation**
    - **Validates: Requirements 3.4.1**
    - Test that loading a valid JSON template and serializing it preserves semantic content
  
  - [x] 3.4 Implement template retrieval methods in TemplateStore
    - Implement get_all_templates() to merge built-in and custom (custom overrides)
    - Implement get_template(name) to retrieve specific template
    - Implement list_templates() returning List[Tuple[name, template, is_custom]]
    - _Requirements: 3.1, 3.4_
  
  - [x] 3.5 Write unit tests for TemplateStore
    - Test built-in templates are loaded correctly
    - Test custom templates override built-in
    - Test invalid JSON handling
    - Test missing directory handling
    - _Requirements: 3.1, 3.4, 3.5_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement template engine with variable replacement
  - [ ] 5.1 Create TemplateEngine class in `harness/templates.py`
    - Initialize with template_store and task_store
    - Define custom exceptions: TemplateNotFoundError, TemplateValidationError, MissingVariableError
    - _Requirements: 3.2_
  
  - [ ] 5.2 Implement _replace_variables() method in TemplateEngine
    - Replace all {variable} placeholders with values from dict
    - Use simple string replacement for each key-value pair
    - _Requirements: 3.2.2_
  
  - [ ]* 5.3 Write property test for variable replacement correctness
    - **Property 2: Variable Replacement Correctness**
    - **Validates: Requirements 3.2.2**
    - Test that replacement handles all variables and no placeholders remain
  
  - [ ] 5.4 Implement _validate_required_variables() method in TemplateEngine
    - Check all required prompt keys are present in provided variables dict
    - Raise MissingVariableError if any required variables missing
    - _Requirements: 3.2.3_
  
  - [ ]* 5.5 Write property test for required field validation
    - **Property 3: Required Field Validation**
    - **Validates: Requirements 3.2.3**
    - Test that validation fails for empty required fields and succeeds otherwise
  
  - [ ] 5.6 Implement _collect_variables_interactive() method in TemplateEngine
    - Iterate through prompts and use click.prompt() for single-line input
    - For multiline prompts, display instructions and read lines until EOFError
    - Apply default values for optional fields when user input is empty
    - Validate required fields are non-empty
    - Return dict of variable values
    - _Requirements: 3.2, 3.3.1_
  
  - [ ] 5.7 Implement create_task_from_template() method in TemplateEngine
    - Load template using template_store.get_template()
    - Validate template and raise TemplateValidationError if invalid
    - Collect variables (interactive or from provided dict)
    - Replace variables in title and description
    - Create Task object with replaced content, template priority/effort, and acceptance_criteria
    - Return created Task
    - _Requirements: 3.2, 3.3_
  
  - [ ]* 5.8 Write integration tests for TemplateEngine
    - Test interactive mode with mocked input
    - Test non-interactive mode with pre-provided variables
    - Test error handling for missing templates
    - Test error handling for invalid templates
    - Test error handling for missing required variables
    - _Requirements: 3.2, 3.3_

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Integrate template commands into CLI
  - [ ] 7.1 Modify `harness plan add` command in `harness/cli.py`
    - Add --template/-t option to specify template name
    - Add --var option (multiple) for non-interactive variable input
    - When --template is provided, initialize TemplateStore and TemplateEngine
    - Parse --var arguments into dict (format: key=value)
    - Call engine.create_task_from_template() with interactive mode based on presence of --var
    - Handle TemplateNotFoundError by displaying available templates
    - Handle TemplateValidationError and MissingVariableError with user-friendly messages
    - Display success message with task ID, title, priority, and effort
    - Maintain backward compatibility with manual task creation (no --template)
    - _Requirements: 3.3.1_
  
  - [ ] 7.2 Create `harness template` command group in `harness/cli.py`
    - Add main template command group using @main.group()
    - _Requirements: 3.3_
  
  - [ ] 7.3 Implement `harness template list` command
    - Initialize TemplateStore
    - Call template_store.list_templates()
    - Display each template with name, description preview, priority, effort
    - Mark custom templates with "(自定义)" suffix
    - Display usage hint at the end
    - _Requirements: 3.3.2_
  
  - [ ] 7.4 Implement `harness template show <template_name>` command
    - Initialize TemplateStore
    - Call template_store.get_template(template_name)
    - Display template metadata: name, title, priority, effort, description
    - Display prompt details: key, required/optional, multiline, default value, question
    - Handle template not found with friendly error message
    - _Requirements: 3.3.3_
  
  - [ ]* 7.5 Write integration tests for CLI commands
    - Test `harness plan add --template feature` with mocked input
    - Test `harness plan add --template bugfix --var` with non-interactive mode
    - Test `harness template list` output format
    - Test `harness template show feature` output
    - Test error handling for invalid template names
    - _Requirements: 3.3_

- [ ] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Add property-based tests for validation rules
  - [ ]* 9.1 Write property test for template field type validation
    - **Property 6: Template Field Type Validation**
    - **Validates: Requirements 3.5.2**
    - Test priority validation, effort range [1,5], prompts non-empty
  
  - [ ]* 9.2 Write property test for variable-prompt consistency
    - **Property 7: Variable-Prompt Consistency**
    - **Validates: Requirements 3.5.3**
    - Test that template variables are subset of prompt keys

- [ ] 10. Final integration and documentation
  - [ ] 10.1 Create example custom template file
    - Create .harness/templates/documentation.json as example
    - Document JSON format in README or docs
    - _Requirements: 3.4_
  
  - [ ] 10.2 Update project documentation
    - Add template system section to docs/api-reference.md
    - Document CLI commands with examples
    - Document custom template format and validation rules
    - Add troubleshooting section for common errors
    - _Requirements: All_
  
  - [ ]* 10.3 Write end-to-end integration tests
    - Test complete workflow: create custom template → use it → verify task
    - Test template override: custom template overrides built-in
    - Test error recovery: invalid custom template doesn't break system
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional (primarily testing tasks) and can be skipped for faster MVP
- Each task references specific requirements from requirements.md for traceability
- Checkpoints ensure incremental validation throughout development
- Property tests validate universal correctness properties from design.md
- Unit tests and integration tests validate specific behaviors and edge cases
- Built-in templates (feature, bugfix, refactor) are defined in code, not JSON files
- Custom templates in .harness/templates/ can override built-in templates
- The implementation uses Python's dataclasses, Click for CLI, and standard library modules (json, pathlib, re)
- Error handling follows graceful degradation: invalid custom templates are skipped with warnings
- Non-interactive mode supports automation and scripting via --var arguments

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["1.3", "1.4"] },
    { "id": 3, "tasks": ["1.5", "1.6", "3.1"] },
    { "id": 4, "tasks": ["3.2"] },
    { "id": 5, "tasks": ["3.3", "3.4"] },
    { "id": 6, "tasks": ["3.5", "5.1"] },
    { "id": 7, "tasks": ["5.2"] },
    { "id": 8, "tasks": ["5.3", "5.4"] },
    { "id": 9, "tasks": ["5.5", "5.6"] },
    { "id": 10, "tasks": ["5.7"] },
    { "id": 11, "tasks": ["5.8", "7.1"] },
    { "id": 12, "tasks": ["7.2"] },
    { "id": 13, "tasks": ["7.3", "7.4"] },
    { "id": 14, "tasks": ["7.5", "9.1", "9.2"] },
    { "id": 15, "tasks": ["10.1", "10.2"] },
    { "id": 16, "tasks": ["10.3"] }
  ]
}
```
