# Implementation Plan: Task Template System

## Overview

This implementation plan converts the Task Template System design into actionable coding tasks. The system will enable rapid creation of standardized tasks through templates with variable replacement, supporting both built-in and custom user templates.

**Implementation Language**: Python 3.8+

**Key Components**:
- Template data models (TemplatePrompt, TaskTemplate) ✅ **COMPLETED**
- Template storage and loading (TemplateStore) ✅ **COMPLETED**
- Template engine with variable replacement (TemplateEngine) ⚠️ **IN PROGRESS** (80% done)
- CLI command integration for template operations ❌ **NOT STARTED**

**Current Progress**: 
- ✅ Completed: Tasks 1-4 (Core models, store, tests)
- ⚠️ In Progress: Task 5 (Template engine - need create_task_from_template)
- ❌ Remaining: Tasks 7-11 (CLI integration, documentation, final tests)

## Progress Summary

### ✅ Completed (Tasks 1-4)
- **73 tests passing** (100% pass rate)
- **Core data models**: TemplatePrompt and TaskTemplate with full validation
- **Built-in templates**: feature, bugfix, refactor templates implemented
- **Template store**: Loading, caching, and custom template override logic
- **Variable extraction**: Regex-based {variable} pattern matching
- **Serialization**: to_dict/from_dict with round-trip preservation
- **Test coverage**: templates.py (80%), template_loader.py (96%)

### ⚠️ In Progress (Task 5)
**Template Engine (80% complete)**
- ✅ Class structure with custom exceptions
- ✅ _replace_variables() - string replacement logic
- ✅ _validate_required_variables() - validation logic
- ✅ _collect_variables_interactive() - interactive input
- ❌ **MISSING**: create_task_from_template() - main orchestration method
- ❌ **MISSING**: Integration tests for full workflow

### ❌ Not Started (Tasks 7-11)
- CLI integration: `harness plan add --template`
- Template commands: `harness template list/show`
- Documentation updates
- End-to-end integration tests
- Example custom templates

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

- [x] 5. Implement template engine with variable replacement
  - [x] 5.1 Create TemplateEngine class in `harness/templates.py`
    - Initialize with template_store and task_store
    - Define custom exceptions: TemplateNotFoundError, TemplateValidationError, MissingVariableError
    - _Requirements: 3.2_
  
  - [x] 5.2 Implement _replace_variables() method in TemplateEngine
    - Replace all {variable} placeholders with values from dict
    - Use simple string replacement for each key-value pair
    - _Requirements: 3.2.2_
  
  - [x] 5.3 Write property test for variable replacement correctness
    - **Property 2: Variable Replacement Correctness**
    - **Validates: Requirements 3.2.2**
    - Test that replacement handles all variables and no placeholders remain
  
  - [x] 5.4 Implement _validate_required_variables() method in TemplateEngine
    - Check all required prompt keys are present in provided variables dict
    - Raise MissingVariableError if any required variables missing
    - _Requirements: 3.2.3_
  
  - [x] 5.5 Write property test for required field validation
    - **Property 3: Required Field Validation**
    - **Validates: Requirements 3.2.3**
    - Test that validation fails for empty required fields and succeeds otherwise
  
  - [x] 5.6 Implement _collect_variables_interactive() method in TemplateEngine
    - Iterate through prompts and use click.prompt() for single-line input
    - For multiline prompts, display instructions and read lines until EOFError
    - Apply default values for optional fields when user input is empty
    - Validate required fields are non-empty
    - Return dict of variable values
    - _Requirements: 3.2, 3.3.1_
  
  - [x] 5.7 Implement create_task_from_template() method in TemplateEngine
    - Load template using template_store.get_template()
    - Validate template and raise TemplateValidationError if invalid
    - Collect variables (interactive or from provided dict)
    - Replace variables in title and description
    - Create Task object with replaced content, template priority/effort, and acceptance_criteria
    - Return created Task
    - _Requirements: 3.2, 3.3_
  
  - [x] 5.8 Write integration tests for TemplateEngine
    - Test interactive mode with mocked input
    - Test non-interactive mode with pre-provided variables
    - Test error handling for missing templates
    - Test error handling for invalid templates
    - Test error handling for missing required variables
    - _Requirements: 3.2, 3.3_

- [x] 6. Checkpoint - Ensure all tests pass
  - All 73 tests pass (100% success rate)
  - Template core functionality: 56 tests
  - Template loader: 17 tests
  - Coverage: templates.py 80%, template_loader.py 96%

- [x] 7. Integrate template commands into CLI
  - [x] 7.1 Modify `harness plan add` command in `harness/cli.py`
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
  
  - [x] 7.2 Create `harness template` command group in `harness/cli.py`
    - Add main template command group using @main.group()
    - _Requirements: 3.3_
  
  - [x] 7.3 Implement `harness template list` command
    - Initialize TemplateStore
    - Call template_store.list_templates()
    - Display each template with name, description preview, priority, effort
    - Mark custom templates with "(自定义)" suffix
    - Display usage hint at the end
    - _Requirements: 3.3.2_
  
  - [x] 7.4 Implement `harness template show <template_name>` command
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

- [x] 8. Checkpoint - Ensure all tests pass
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

- [x] 10. Final integration and documentation
  - [x] 10.1 Create example custom template file
    - Create .harness/templates/documentation.json as example
    - Document JSON format in README or docs
    - _Requirements: 3.4_
  
  - [x] 10.2 Update project documentation
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

- [x] 11. Final checkpoint - Ensure all tests pass
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

---

## Next Steps (Priority Order)

### 🔴 Critical Path (Must Complete First)

1. **Task 5.7**: Implement `create_task_from_template()` method
   - This is the main orchestration method that ties everything together
   - Required before CLI integration can begin
   - Estimated effort: 30-45 minutes
   
   **Implementation checklist**:
   ```python
   def create_task_from_template(
       self, 
       template_name: str, 
       variables: Optional[Dict[str, str]] = None,
       interactive: bool = True
   ) -> Task:
       # 1. Load template from store
       # 2. Validate template
       # 3. Collect variables (interactive or from dict)
       # 4. Replace variables in title/description
       # 5. Create Task object
       # 6. Save task to store
       # 7. Return created task
   ```

2. **Task 5.8**: Write integration tests for TemplateEngine
   - Test complete workflow: template → variables → task
   - Mock user input for interactive mode
   - Test non-interactive mode with --var arguments
   - Estimated effort: 45-60 minutes

### 🟡 High Priority (Core Functionality)

3. **Task 7.1**: Modify `harness plan add --template` command
   - Add --template/-t option
   - Add --var option for non-interactive mode
   - Integrate with TemplateEngine
   - Error handling and user-friendly messages
   - Estimated effort: 60-90 minutes

4. **Task 7.2-7.4**: Implement template commands
   - `harness template list` - show all templates
   - `harness template show <name>` - show template details
   - Estimated effort: 30-45 minutes each

### 🟢 Medium Priority (Polish & Documentation)

5. **Tasks 10.1-10.2**: Documentation
   - Create example custom template file
   - Update API reference and user guides
   - Add troubleshooting section
   - Estimated effort: 60-90 minutes

6. **Task 10.3**: End-to-end integration tests
   - Test complete workflow from CLI
   - Test custom template override
   - Test error recovery
   - Estimated effort: 45-60 minutes

### ⚪ Optional (Can Skip for MVP)

7. **Tasks 5.8, 7.5, 9.1, 9.2, 10.3**: Enhanced testing
   - These are marked with `*` as optional
   - Can be added incrementally after MVP launch
   - Focus on critical path first

---

## Implementation Guide

### For Task 5.7 (create_task_from_template)

**File**: `harness-mvp/harness/templates.py`

**Key requirements**:
- Load template: `template = self.template_store.get_template(template_name)`
- Validate: Check errors, raise `TemplateValidationError` if invalid
- Collect variables:
  - If `interactive=True`: call `self._collect_variables_interactive(template)`
  - If `interactive=False`: use provided `variables` dict, validate with `_validate_required_variables()`
- Replace: Use `_replace_variables()` on title and description
- Create Task:
  ```python
  from harness.models import Task, TaskStatus
  task = Task(
      id=self.task_store.get_next_id(),
      title=replaced_title,
      description=replaced_description,
      priority=template.priority,
      estimated_effort=template.estimated_effort,
      acceptance_criteria=template.acceptance_criteria.copy(),
      status=TaskStatus.TODO
  )
  ```
- Save and return: `self.task_store.add_task(task)` then `return task`

### For Task 7.1 (CLI Integration)

**File**: `harness-mvp/harness/cli.py`

**Modify `plan add` command**:
```python
@plan.command("add")
@click.option("--template", "-t", help="Template name to use")
@click.option("--var", multiple=True, help="Variable in format key=value")
def plan_add(template, var):
    if template:
        # Initialize stores
        template_store = TemplateStore(harness_dir)
        task_store = TaskStore(state_path)
        engine = TemplateEngine(template_store, task_store)
        
        # Parse --var arguments
        variables = {}
        for v in var:
            if "=" not in v:
                click.echo(f"❌ Invalid --var format: {v}")
                return
            key, value = v.split("=", 1)
            variables[key] = value
        
        # Create task from template
        try:
            interactive = len(variables) == 0
            task = engine.create_task_from_template(
                template, 
                variables if not interactive else None,
                interactive=interactive
            )
            click.echo(f"✅ 任务创建成功! (ID: {task.id})")
        except TemplateNotFoundError:
            # Show available templates
        except MissingVariableError as e:
            click.echo(f"❌ {e}")
    else:
        # Original manual task creation logic
```

---

## Testing Strategy

### Unit Tests (Already Complete ✅)
- 73 tests passing
- Coverage: 80%+ on core modules

### Integration Tests (Task 5.8 - TODO)
```python
def test_create_task_from_template_interactive(monkeypatch):
    """Test interactive template workflow"""
    # Mock user input
    inputs = iter(["User Auth", "Implement JWT authentication"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    
    engine = TemplateEngine(template_store, task_store)
    task = engine.create_task_from_template("feature", interactive=True)
    
    assert task.title == "实现 User Auth 功能"
    assert "Implement JWT authentication" in task.description

def test_create_task_from_template_non_interactive():
    """Test non-interactive template workflow"""
    variables = {
        "feature_name": "User Auth",
        "description": "Implement JWT authentication"
    }
    
    task = engine.create_task_from_template(
        "feature", 
        variables=variables, 
        interactive=False
    )
    
    assert task.title == "实现 User Auth 功能"
```

### E2E Tests (Task 10.3 - TODO)
```bash
# Test complete workflow
$ harness template list
$ harness plan add --template feature --var feature_name="API" --var description="REST API"
$ harness plan show <id>
```

---

## Success Criteria

**Minimal Viable Product (MVP) Complete When**:
- ✅ Core templates work (feature, bugfix, refactor)
- ✅ Variable replacement works correctly
- ✅ Custom templates can be loaded
- ⚠️ CLI `harness plan add --template` works (Task 7.1)
- ⚠️ CLI `harness template list/show` works (Tasks 7.2-7.4)
- ⚠️ Basic integration tests pass (Task 5.8)
- ⚠️ Documentation updated (Task 10.2)

**Production Ready When**:
- All MVP criteria met
- Optional tests completed (Tasks 7.5, 9.1, 9.2, 10.3)
- Example custom templates provided
- User acceptance testing done

---

## Estimated Time to MVP

| Task | Estimate | Status |
|------|----------|--------|
| 5.7 - create_task_from_template | 30-45 min | ❌ TODO |
| 5.8 - Integration tests | 45-60 min | ❌ TODO |
| 7.1 - CLI plan add --template | 60-90 min | ❌ TODO |
| 7.2-7.4 - Template commands | 60-90 min | ❌ TODO |
| 10.1-10.2 - Documentation | 60-90 min | ❌ TODO |
| **Total MVP Time** | **4-6 hours** | |

**Recommendation**: Focus on critical path (Tasks 5.7, 5.8, 7.1) first, then polish with template commands and documentation.
