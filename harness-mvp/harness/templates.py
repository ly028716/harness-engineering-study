"""任务模板系统 - 数据模型和模板引擎"""
import re
import click
from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict, Any

from harness.models import Priority


@dataclass
class TemplatePrompt:
    """Represents a template variable prompt configuration"""
    key: str                    # Variable name (e.g., "feature_name")
    question: str               # Prompt text for user
    required: bool = True       # Whether input is mandatory
    multiline: bool = False     # Whether to accept multi-line input
    default: Optional[str] = None  # Default value if not provided
    
    def validate(self) -> List[str]:
        """Validate prompt configuration
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Validate key is not empty
        if not self.key or not self.key.strip():
            errors.append("Prompt key cannot be empty")
        
        # Validate key format (valid Python identifier)
        if self.key and not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.key):
            errors.append(f"Invalid key '{self.key}': must be valid identifier")
        
        # Validate question is not empty
        if not self.question or not self.question.strip():
            errors.append(f"Question for '{self.key}' cannot be empty")
        
        return errors


@dataclass
class TaskTemplate:
    """Represents a task template"""
    name: str                          # Template identifier
    title: str                         # Task title with variables
    description: str                   # Task description with variables
    priority: Priority                 # Default priority
    estimated_effort: int              # Default effort (1-5)
    prompts: List[TemplatePrompt]      # Variable prompts
    acceptance_criteria: List[str] = field(default_factory=list)
    
    def get_variables(self) -> Set[str]:
        r"""Extract all {variable} placeholders from title and description
        
        Uses regex pattern: \{([a-zA-Z_][a-zA-Z0-9_]*)\}
        
        Returns:
            Set of variable names found in title and description
        """
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        variables = set()
        
        # Extract variables from title
        variables.update(re.findall(pattern, self.title))
        
        # Extract variables from description
        variables.update(re.findall(pattern, self.description))
        
        return variables
    
    def validate(self) -> List[str]:
        """Validate template structure and consistency
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Validate required fields
        if not self.name or not self.name.strip():
            errors.append("Template name cannot be empty")
        
        # Validate name format (letters, numbers, underscore, hyphen only)
        if self.name and not re.match(r'^[a-zA-Z0-9_-]+$', self.name):
            errors.append(f"Invalid name '{self.name}': use only letters, numbers, _, -")
        
        if not self.title or not self.title.strip():
            errors.append("Template title cannot be empty")
        
        if not self.description or not self.description.strip():
            errors.append("Template description cannot be empty")
        
        # Validate effort range [1-5]
        if not (1 <= self.estimated_effort <= 5):
            errors.append(f"Estimated effort must be 1-5, got {self.estimated_effort}")
        
        # Validate prompts is non-empty
        if not self.prompts:
            errors.append("Template must have at least one prompt")
        
        # Validate each prompt and check for duplicates
        prompt_keys = set()
        for prompt in self.prompts:
            prompt_errors = prompt.validate()
            errors.extend(prompt_errors)
            
            if prompt.key in prompt_keys:
                errors.append(f"Duplicate prompt key: {prompt.key}")
            prompt_keys.add(prompt.key)
        
        # Validate variable-prompt consistency
        # All template variables must be defined in prompts
        template_vars = self.get_variables()
        prompt_keys_set = {p.key for p in self.prompts}
        
        undefined_vars = template_vars - prompt_keys_set
        if undefined_vars:
            errors.append(f"Variables not defined in prompts: {undefined_vars}")
        
        # Warn about unused prompts (prompts not used in template)
        unused_prompts = prompt_keys_set - template_vars
        if unused_prompts:
            errors.append(f"Warning: Prompts not used in template: {unused_prompts}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON storage
        
        Returns:
            Dictionary representation of the template
        """
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "estimated_effort": self.estimated_effort,
            "acceptance_criteria": self.acceptance_criteria,
            "prompts": [
                {
                    "key": p.key,
                    "question": p.question,
                    "required": p.required,
                    "multiline": p.multiline,
                    "default": p.default
                }
                for p in self.prompts
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskTemplate":
        """Deserialize from dictionary
        
        Args:
            data: Dictionary containing template data
            
        Returns:
            TaskTemplate instance
        """
        prompts = [
            TemplatePrompt(
                key=p["key"],
                question=p["question"],
                required=p.get("required", True),
                multiline=p.get("multiline", False),
                default=p.get("default")
            )
            for p in data.get("prompts", [])
        ]
        
        return cls(
            name=data["name"],
            title=data["title"],
            description=data["description"],
            priority=Priority.from_string(data.get("priority", "REQUIRED")),
            estimated_effort=data.get("estimated_effort", 1),
            prompts=prompts,
            acceptance_criteria=data.get("acceptance_criteria", [])
        )


# Custom Exceptions for Template Engine

class TemplateNotFoundError(Exception):
    """Raised when a requested template does not exist"""
    pass


class TemplateValidationError(Exception):
    """Raised when a template fails validation"""
    pass


class MissingVariableError(Exception):
    """Raised when required variables are not provided"""
    pass


class TemplateEngine:
    """Orchestrates template-based task creation"""
    
    def __init__(self, template_store, task_store):
        """Initialize template engine
        
        Args:
            template_store: TemplateStore instance for loading templates
            task_store: TaskStore instance for creating tasks
        """
        self.template_store = template_store
        self.task_store = task_store
    
    def _replace_variables(self, text: str, variables: Dict[str, str]) -> str:
        """Replace {variable} placeholders with actual values
        
        Args:
            text: Text containing {variable} placeholders
            variables: Dictionary mapping variable names to replacement values
            
        Returns:
            Text with all placeholders replaced by their values
        """
        result = text
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, value)
        return result
    
    def _validate_required_variables(
        self, 
        template: TaskTemplate, 
        variables: Dict[str, str]
    ) -> None:
        """Validate that all required variables are provided
        
        Checks that all required prompt keys are present in the provided
        variables dictionary. This is essential for non-interactive mode
        where user cannot be prompted for missing values.
        
        Args:
            template: TaskTemplate to validate against
            variables: Dictionary of provided variable values
            
        Raises:
            MissingVariableError: If any required variables are missing
        """
        # Collect all required prompt keys
        required_keys = {p.key for p in template.prompts if p.required}
        
        # Check which keys are provided
        provided_keys = set(variables.keys())
        
        # Find missing required variables
        missing = required_keys - provided_keys
        
        if missing:
            raise MissingVariableError(f"Missing required variables: {missing}")
    
    def _collect_variables_interactive(self, template: TaskTemplate) -> Dict[str, str]:
        """Prompt user for variable values interactively
        
        Iterates through all prompts in the template and collects user input.
        Supports both single-line and multiline inputs, applies default values
        for optional fields, and validates that required fields are non-empty.
        
        Args:
            template: TaskTemplate containing the prompts to display
            
        Returns:
            Dictionary mapping variable keys to user-provided values
            
        Raises:
            MissingVariableError: If a required variable is left empty
        """
        values = {}
        
        # Display template name header
        click.echo(f"\n✨ 使用模板: {template.name}\n")
        
        # Iterate through each prompt in the template
        for prompt in template.prompts:
            if prompt.multiline:
                # Multiline input mode
                click.echo(f"{prompt.question} (多行输入，按 Ctrl+D 或 Ctrl+Z 结束):")
                lines = []
                try:
                    while True:
                        line = input("> ")
                        lines.append(line)
                except EOFError:
                    # User pressed Ctrl+D (Unix) or Ctrl+Z (Windows)
                    pass
                value = "\n".join(lines)
            else:
                # Single-line input mode
                if prompt.default:
                    # Use click.prompt with default value
                    value = click.prompt(
                        prompt.question,
                        default=prompt.default,
                        show_default=True
                    )
                else:
                    # Use click.prompt without default
                    value = click.prompt(prompt.question)
            
            # Validate required fields
            if prompt.required and not value.strip():
                if prompt.default:
                    # Use default value for optional field with default
                    value = prompt.default
                else:
                    # Raise error for required field without value
                    raise MissingVariableError(f"Required variable '{prompt.key}' cannot be empty")
            
            # Store the stripped value
            values[prompt.key] = value.strip()
        
        return values
    
    def create_task_from_template(
        self,
        template_name: str,
        variables: Optional[Dict[str, str]] = None,
        interactive: bool = True
    ):
        """Create a task from template
        
        Args:
            template_name: Name of template to use
            variables: Pre-provided variable values (for non-interactive mode)
            interactive: Whether to prompt user for missing variables
        
        Returns:
            Created Task object
        
        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateValidationError: If template is invalid
            MissingVariableError: If required variables not provided in non-interactive mode
        """
        from harness.models import Task
        
        # Load template using template_store.get_template()
        template = self.template_store.get_template(template_name)
        if not template:
            raise TemplateNotFoundError(f"Template '{template_name}' not found")
        
        # Validate template and raise TemplateValidationError if invalid
        errors = template.validate()
        if errors:
            raise TemplateValidationError(f"Template validation failed: {errors}")
        
        # Collect variables (interactive or from provided dict)
        if interactive:
            var_values = self._collect_variables_interactive(template)
        else:
            # Use provided variables dict
            if variables is None:
                variables = {}
            # Validate required variables are provided
            self._validate_required_variables(template, variables)
            var_values = variables
        
        # Replace variables in title and description
        title = self._replace_variables(template.title, var_values)
        description = self._replace_variables(template.description, var_values)
        
        # Create Task object with:
        # - id from task_store.get_next_task_id()
        # - replaced title and description
        # - template's priority and effort
        # - acceptance_criteria from template
        task = Task(
            id=self.task_store.get_next_task_id(),
            title=title,
            description=description,
            priority=template.priority,
            estimated_effort=template.estimated_effort,
            acceptance_criteria=template.acceptance_criteria.copy()
        )
        
        # Return created Task
        return task
