"""任务模板系统 - 数据模型和模板引擎"""
import re
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
