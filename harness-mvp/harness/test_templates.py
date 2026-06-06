"""Unit tests for template system - Task 1.1 TemplatePrompt and Task 1.2 TaskTemplate tests"""
import pytest
import re
from hypothesis import given, strategies as st
from harness.templates import TemplatePrompt, TaskTemplate, Priority, TemplateEngine, MissingVariableError
from unittest.mock import Mock


class TestTemplatePrompt:
    """Test suite for TemplatePrompt class (Task 1.1)"""
    
    def test_valid_prompt_passes_validation(self):
        """Test that a valid TemplatePrompt passes validation"""
        prompt = TemplatePrompt(
            key="feature_name",
            question="What is the feature name?",
            required=True,
            multiline=False,
            default=None
        )
        
        errors = prompt.validate()
        assert errors == []
    
    def test_validate_rejects_empty_key(self):
        """Test that validate() rejects empty key"""
        prompt = TemplatePrompt(
            key="",
            question="Question?",
            required=True
        )
        
        errors = prompt.validate()
        assert any("key cannot be empty" in err for err in errors)
    
    def test_validate_rejects_whitespace_only_key(self):
        """Test that validate() rejects whitespace-only key"""
        prompt = TemplatePrompt(
            key="   ",
            question="Question?",
            required=True
        )
        
        errors = prompt.validate()
        assert any("key cannot be empty" in err for err in errors)
    
    def test_validate_rejects_key_starting_with_number(self):
        """Test that validate() rejects key starting with a number"""
        prompt = TemplatePrompt(
            key="123invalid",
            question="Question?",
            required=True
        )
        
        errors = prompt.validate()
        assert any("must be valid identifier" in err for err in errors)
    
    def test_validate_rejects_key_with_special_characters(self):
        """Test that validate() rejects key with special characters"""
        invalid_keys = [
            "key-with-dash",
            "key with space",
            "key@special",
            "key!exclaim",
            "key.dot"
        ]
        
        for key in invalid_keys:
            prompt = TemplatePrompt(key=key, question="Question?")
            errors = prompt.validate()
            assert any("must be valid identifier" in err for err in errors), \
                f"Key '{key}' should be rejected"
    
    def test_validate_accepts_valid_identifier_keys(self):
        """Test that validate() accepts valid Python identifier keys"""
        valid_keys = [
            "feature_name",
            "_private",
            "CamelCase",
            "snake_case",
            "var123",
            "VAR_123"
        ]
        
        for key in valid_keys:
            prompt = TemplatePrompt(key=key, question="Question?")
            errors = prompt.validate()
            assert errors == [], f"Key '{key}' should be valid but got errors: {errors}"
    
    def test_validate_rejects_empty_question(self):
        """Test that validate() rejects empty question"""
        prompt = TemplatePrompt(
            key="valid_key",
            question="",
            required=True
        )
        
        errors = prompt.validate()
        assert any("Question" in err and "cannot be empty" in err for err in errors)
    
    def test_validate_rejects_whitespace_only_question(self):
        """Test that validate() rejects whitespace-only question"""
        prompt = TemplatePrompt(
            key="valid_key",
            question="   ",
            required=True
        )
        
        errors = prompt.validate()
        assert any("Question" in err and "cannot be empty" in err for err in errors)
    
    def test_validate_with_both_empty_key_and_question(self):
        """Test that validate() reports both empty key and empty question"""
        prompt = TemplatePrompt(
            key="",
            question="",
            required=True
        )
        
        errors = prompt.validate()
        # Should have multiple errors
        assert len(errors) >= 2
        assert any("key cannot be empty" in err for err in errors)
        assert any("Question" in err and "cannot be empty" in err for err in errors)
    
    def test_default_values(self):
        """Test that TemplatePrompt has correct default values"""
        prompt = TemplatePrompt(
            key="test_key",
            question="Test question?"
        )
        
        assert prompt.required is True  # Default
        assert prompt.multiline is False  # Default
        assert prompt.default is None  # Default
    
    def test_optional_prompt_with_default(self):
        """Test TemplatePrompt with optional field and default value"""
        prompt = TemplatePrompt(
            key="optional_field",
            question="Optional question?",
            required=False,
            multiline=True,
            default="default_value"
        )
        
        errors = prompt.validate()
        assert errors == []
        assert prompt.required is False
        assert prompt.multiline is True
        assert prompt.default == "default_value"


class TestTaskTemplate:
    """Test suite for TaskTemplate class"""
    
    def test_get_variables_extracts_from_title_and_description(self):
        """Test that get_variables() extracts all variables from title and description"""
        template = TaskTemplate(
            name="test",
            title="Implement {feature_name} feature",
            description="Add {feature_name} with {component} to the system",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("feature_name", "Enter feature name"),
                TemplatePrompt("component", "Enter component")
            ]
        )
        
        variables = template.get_variables()
        assert variables == {"feature_name", "component"}
    
    def test_get_variables_returns_empty_set_when_no_variables(self):
        """Test that get_variables() returns empty set when no variables present"""
        template = TaskTemplate(
            name="test",
            title="Simple title",
            description="Simple description",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[TemplatePrompt("dummy", "Dummy question")]
        )
        
        variables = template.get_variables()
        assert variables == set()
    
    def test_get_variables_handles_duplicate_variables(self):
        """Test that get_variables() handles duplicate variable occurrences"""
        template = TaskTemplate(
            name="test",
            title="Implement {feature} feature",
            description="The {feature} should work with {feature} properly",
            priority=Priority.REQUIRED,
            estimated_effort=2,
            prompts=[TemplatePrompt("feature", "Feature name")]
        )
        
        variables = template.get_variables()
        # Should return unique variables only
        assert variables == {"feature"}
    
    def test_get_variables_matches_valid_identifier_pattern(self):
        """Test that get_variables() only matches valid Python identifiers"""
        template = TaskTemplate(
            name="test",
            title="{valid_var} and {_private} and {CamelCase}",
            description="{123invalid} {with-dash} {with space}",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("valid_var", "Q1"),
                TemplatePrompt("_private", "Q2"),
                TemplatePrompt("CamelCase", "Q3")
            ]
        )
        
        variables = template.get_variables()
        # Should only match valid identifiers (starting with letter or underscore)
        assert variables == {"valid_var", "_private", "CamelCase"}
    
    def test_to_dict_serializes_all_fields(self):
        """Test that to_dict() serializes all template fields correctly"""
        prompts = [
            TemplatePrompt("var1", "Question 1", required=True, multiline=False, default=None),
            TemplatePrompt("var2", "Question 2", required=False, multiline=True, default="default_val")
        ]
        
        template = TaskTemplate(
            name="feature",
            title="Implement {var1}",
            description="Description {var2}",
            priority=Priority.RECOMMENDED,
            estimated_effort=4,
            prompts=prompts,
            acceptance_criteria=["Criterion 1", "Criterion 2"]
        )
        
        result = template.to_dict()
        
        assert result["name"] == "feature"
        assert result["title"] == "Implement {var1}"
        assert result["description"] == "Description {var2}"
        assert result["priority"] == "RECOMMENDED"
        assert result["estimated_effort"] == 4
        assert result["acceptance_criteria"] == ["Criterion 1", "Criterion 2"]
        assert len(result["prompts"]) == 2
        assert result["prompts"][0]["key"] == "var1"
        assert result["prompts"][0]["question"] == "Question 1"
        assert result["prompts"][0]["required"] is True
        assert result["prompts"][0]["multiline"] is False
        assert result["prompts"][0]["default"] is None
        assert result["prompts"][1]["key"] == "var2"
        assert result["prompts"][1]["default"] == "default_val"
    
    def test_from_dict_deserializes_correctly(self):
        """Test that from_dict() correctly deserializes template data"""
        data = {
            "name": "bugfix",
            "title": "Fix {bug_name}",
            "description": "Fix the bug: {bug_description}",
            "priority": "REQUIRED",
            "estimated_effort": 2,
            "acceptance_criteria": ["Bug fixed", "Tests pass"],
            "prompts": [
                {
                    "key": "bug_name",
                    "question": "Bug name?",
                    "required": True,
                    "multiline": False,
                    "default": None
                },
                {
                    "key": "bug_description",
                    "question": "Description?",
                    "required": False,
                    "multiline": True,
                    "default": "TBD"
                }
            ]
        }
        
        template = TaskTemplate.from_dict(data)
        
        assert template.name == "bugfix"
        assert template.title == "Fix {bug_name}"
        assert template.description == "Fix the bug: {bug_description}"
        assert template.priority == Priority.REQUIRED
        assert template.estimated_effort == 2
        assert template.acceptance_criteria == ["Bug fixed", "Tests pass"]
        assert len(template.prompts) == 2
        assert template.prompts[0].key == "bug_name"
        assert template.prompts[0].question == "Bug name?"
        assert template.prompts[0].required is True
        assert template.prompts[1].multiline is True
        assert template.prompts[1].default == "TBD"
    
    def test_from_dict_uses_defaults_for_optional_fields(self):
        """Test that from_dict() uses default values for optional fields"""
        data = {
            "name": "minimal",
            "title": "Title",
            "description": "Description",
            "prompts": []
        }
        
        template = TaskTemplate.from_dict(data)
        
        assert template.priority == Priority.REQUIRED  # default
        assert template.estimated_effort == 1  # default
        assert template.acceptance_criteria == []  # default
    
    def test_serialization_round_trip_preserves_data(self):
        """Test that to_dict() -> from_dict() preserves template data"""
        original = TaskTemplate(
            name="refactor",
            title="Refactor {module}",
            description="Clean up {module} code",
            priority=Priority.OPTIONAL,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("module", "Module name?", required=True, multiline=False)
            ],
            acceptance_criteria=["Code cleaner", "Tests pass"]
        )
        
        # Serialize and deserialize
        data = original.to_dict()
        restored = TaskTemplate.from_dict(data)
        
        # Compare fields
        assert restored.name == original.name
        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.priority == original.priority
        assert restored.estimated_effort == original.estimated_effort
        assert restored.acceptance_criteria == original.acceptance_criteria
        assert len(restored.prompts) == len(original.prompts)
        assert restored.prompts[0].key == original.prompts[0].key
        assert restored.prompts[0].question == original.prompts[0].question
        assert restored.prompts[0].required == original.prompts[0].required
    
    def test_validate_accepts_valid_template(self):
        """Test that validate() returns no errors for a valid template"""
        template = TaskTemplate(
            name="valid-template",
            title="Implement {feature}",
            description="Add {feature} functionality",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[TemplatePrompt("feature", "Feature name?")]
        )
        
        errors = template.validate()
        assert errors == []
    
    def test_validate_rejects_empty_name(self):
        """Test that validate() rejects empty template name"""
        template = TaskTemplate(
            name="",
            title="Title",
            description="Description",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[TemplatePrompt("var", "Question")]
        )
        
        errors = template.validate()
        assert any("name cannot be empty" in err for err in errors)
    
    def test_validate_rejects_invalid_name_format(self):
        """Test that validate() rejects invalid name format"""
        template = TaskTemplate(
            name="invalid name!",
            title="Title",
            description="Description",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[TemplatePrompt("var", "Question")]
        )
        
        errors = template.validate()
        assert any("Invalid name" in err for err in errors)
    
    def test_validate_accepts_valid_name_formats(self):
        """Test that validate() accepts valid name formats"""
        valid_names = ["feature", "bug-fix", "refactor_code", "API-v2"]
        
        for name in valid_names:
            template = TaskTemplate(
                name=name,
                title="Title {var}",
                description="Description",
                priority=Priority.REQUIRED,
                estimated_effort=1,
                prompts=[TemplatePrompt("var", "Question")]
            )
            errors = template.validate()
            # Should not have name-related errors
            assert not any("Invalid name" in err for err in errors), f"Name '{name}' should be valid"
    
    def test_validate_rejects_effort_out_of_range(self):
        """Test that validate() rejects estimated_effort outside [1-5] range"""
        template_too_low = TaskTemplate(
            name="test",
            title="Title",
            description="Description",
            priority=Priority.REQUIRED,
            estimated_effort=0,
            prompts=[TemplatePrompt("var", "Question")]
        )
        
        template_too_high = TaskTemplate(
            name="test",
            title="Title",
            description="Description",
            priority=Priority.REQUIRED,
            estimated_effort=6,
            prompts=[TemplatePrompt("var", "Question")]
        )
        
        errors_low = template_too_low.validate()
        errors_high = template_too_high.validate()
        
        assert any("must be 1-5" in err for err in errors_low)
        assert any("must be 1-5" in err for err in errors_high)
    
    def test_validate_rejects_empty_prompts_list(self):
        """Test that validate() rejects empty prompts list"""
        template = TaskTemplate(
            name="test",
            title="Title",
            description="Description",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[]
        )
        
        errors = template.validate()
        assert any("at least one prompt" in err for err in errors)
    
    def test_validate_checks_variable_prompt_consistency(self):
        """Test that validate() checks all template variables are defined in prompts"""
        template = TaskTemplate(
            name="test",
            title="Implement {feature} and {component}",
            description="Add {feature} functionality",
            priority=Priority.REQUIRED,
            estimated_effort=2,
            prompts=[
                TemplatePrompt("feature", "Feature name?")
                # Missing: component
            ]
        )
        
        errors = template.validate()
        assert any("not defined in prompts" in err and "component" in err for err in errors)
    
    def test_validate_warns_about_unused_prompts(self):
        """Test that validate() warns about prompts not used in template"""
        template = TaskTemplate(
            name="test",
            title="Simple title",
            description="Simple description",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("unused_var", "This variable is not used")
            ]
        )
        
        errors = template.validate()
        assert any("not used in template" in err and "unused_var" in err for err in errors)
    
    def test_validate_detects_duplicate_prompt_keys(self):
        """Test that validate() detects duplicate prompt keys"""
        template = TaskTemplate(
            name="test",
            title="Title {var}",
            description="Description",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("var", "Question 1"),
                TemplatePrompt("var", "Question 2")  # Duplicate
            ]
        )
        
        errors = template.validate()
        assert any("Duplicate prompt key" in err for err in errors)



class TestTaskTemplateProperties:
    """Property-based tests for TaskTemplate using Hypothesis"""
    
    # Strategy for generating valid variable identifiers
    # Must match: [a-zA-Z_][a-zA-Z0-9_]*
    @staticmethod
    def valid_identifier():
        """Generate valid Python identifiers for variable names"""
        # First character: letter or underscore
        first_char = st.sampled_from('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
        # Subsequent characters: letter, digit, or underscore
        rest_chars = st.text(
            alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_',
            min_size=0,
            max_size=20
        )
        return st.builds(lambda f, r: f + r, first_char, rest_chars)
    
    @staticmethod
    def invalid_variable_pattern():
        """Generate invalid variable patterns that should NOT be extracted"""
        return st.one_of(
            # Numbers at start
            st.builds(lambda n, rest: f"{{{n}{rest}}}", 
                     st.integers(0, 9), 
                     st.text(alphabet='abcdefghijklmnopqrstuvwxyz', max_size=10)),
            # Contains hyphens
            st.builds(lambda parts: f"{{{'-'.join(parts)}}}", 
                     st.lists(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=5), min_size=2, max_size=3)),
            # Contains spaces
            st.builds(lambda parts: f"{{{' '.join(parts)}}}", 
                     st.lists(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=5), min_size=2, max_size=3)),
            # Contains special characters (excluding '}' to avoid creating valid subpatterns)
            st.builds(lambda name, char: f"{{{name}{char}}}", 
                     st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=10),
                     st.sampled_from(['@', '!', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '=', '[', ']', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/'])),
            # Empty braces
            st.just("{}"),
            # Only whitespace
            st.just("{   }")
        )
    
    @given(
        valid_vars=st.lists(valid_identifier(), min_size=0, max_size=10, unique=True),
        title_template=st.text(min_size=0, max_size=100),
        desc_template=st.text(min_size=0, max_size=200)
    )
    def test_variable_extraction_completeness(self, valid_vars, title_template, desc_template):
        """
        **Property 1: Variable Extraction Completeness**
        **Validates: Requirements 3.2.1**
        
        Test that get_variables() extracts ALL valid {variable} patterns.
        
        For any template text containing {variable} placeholders with valid identifiers,
        get_variables() should extract exactly those variables and no others.
        """
        # Inject valid variables into the title and description
        # We'll scatter them throughout the text
        title_with_vars = title_template
        desc_with_vars = desc_template
        
        expected_vars = set()
        
        # Add valid variables to title
        for i, var in enumerate(valid_vars[:len(valid_vars)//2 + 1]):
            placeholder = f"{{{var}}}"
            title_with_vars += f" {placeholder}"
            expected_vars.add(var)
        
        # Add valid variables to description (some may duplicate title vars)
        for var in valid_vars[len(valid_vars)//2:]:
            placeholder = f"{{{var}}}"
            desc_with_vars += f" {placeholder}"
            expected_vars.add(var)
        
        # Create template with these text fields
        # We need at least one prompt, so create a dummy one
        template = TaskTemplate(
            name="test",
            title=title_with_vars,
            description=desc_with_vars,
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[TemplatePrompt("dummy", "Dummy question")]
        )
        
        # Extract variables
        extracted = template.get_variables()
        
        # Verify completeness: extracted should contain all expected valid variables
        assert expected_vars.issubset(extracted), \
            f"get_variables() failed to extract all valid variables. Expected: {expected_vars}, Got: {extracted}"
        
        # Verify correctness: extracted should ONLY contain valid identifiers
        # Check that each extracted variable matches the valid pattern
        pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        for var in extracted:
            assert pattern.match(var), \
                f"get_variables() extracted invalid identifier: '{var}'"
    
    @given(
        valid_vars=st.lists(valid_identifier(), min_size=1, max_size=5, unique=True),
        invalid_patterns=st.lists(invalid_variable_pattern(), min_size=1, max_size=5)
    )
    def test_variable_extraction_rejects_invalid_patterns(self, valid_vars, invalid_patterns):
        """
        **Property 1: Variable Extraction Completeness (Part 2)**
        **Validates: Requirements 3.2.1**
        
        Test that get_variables() does NOT extract invalid {variable} patterns.
        
        Invalid patterns include:
        - {123var} (starts with number)
        - {var-name} (contains hyphen)
        - {var name} (contains space)
        - {var@special} (contains special characters)
        - {} (empty)
        """
        # Create text with mix of valid and invalid patterns
        title_parts = []
        desc_parts = []
        
        expected_vars = set()
        
        # Add valid variables
        for var in valid_vars:
            title_parts.append(f"{{{var}}}")
            expected_vars.add(var)
        
        # Add invalid patterns
        for invalid in invalid_patterns:
            desc_parts.append(invalid)
        
        title = " ".join(title_parts)
        description = " ".join(desc_parts)
        
        template = TaskTemplate(
            name="test",
            title=title,
            description=description,
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[TemplatePrompt("dummy", "Dummy question")]
        )
        
        extracted = template.get_variables()
        
        # Should extract ONLY valid variables, not invalid patterns
        assert extracted == expected_vars, \
            f"get_variables() should extract only valid variables. Expected: {expected_vars}, Got: {extracted}"
    
    @given(
        var_name=valid_identifier(),
        occurrences=st.integers(min_value=1, max_value=10)
    )
    def test_variable_extraction_handles_duplicates(self, var_name, occurrences):
        """
        **Property 1: Variable Extraction Completeness (Part 3)**
        **Validates: Requirements 3.2.1**
        
        Test that get_variables() returns unique variables even with duplicates.
        """
        # Create template with same variable repeated multiple times
        title = " ".join([f"{{{var_name}}}"] * occurrences)
        description = " ".join([f"{{{var_name}}}"] * occurrences)
        
        template = TaskTemplate(
            name="test",
            title=title,
            description=description,
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[TemplatePrompt("dummy", "Dummy question")]
        )
        
        extracted = template.get_variables()
        
        # Should return only unique variable name, not duplicates
        assert extracted == {var_name}, \
            f"get_variables() should return unique variables. Expected: {{{var_name}}}, Got: {extracted}"
        assert len(extracted) == 1, \
            f"get_variables() should deduplicate. Expected 1 variable, got {len(extracted)}"
    
    @given(st.text(min_size=0, max_size=200))
    def test_variable_extraction_on_text_without_variables(self, text):
        """
        **Property 1: Variable Extraction Completeness (Part 4)**
        **Validates: Requirements 3.2.1**
        
        Test that get_variables() returns empty set for text without valid variables.
        """
        # Ensure text doesn't contain valid variable patterns by escaping braces
        # or using text that doesn't have the pattern
        safe_text = text.replace('{', '{{').replace('}', '}}')
        
        template = TaskTemplate(
            name="test",
            title=safe_text[:100] if len(safe_text) > 100 else safe_text,
            description=safe_text,
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[TemplatePrompt("dummy", "Dummy question")]
        )
        
        extracted = template.get_variables()
        
        # Should return empty set when no variables present
        assert extracted == set(), \
            f"get_variables() should return empty set for text without variables. Got: {extracted}"
    
    @given(
        title_vars=st.lists(valid_identifier(), min_size=1, max_size=5, unique=True),
        desc_vars=st.lists(valid_identifier(), min_size=1, max_size=5, unique=True)
    )
    def test_variable_extraction_from_both_title_and_description(self, title_vars, desc_vars):
        """
        **Property 1: Variable Extraction Completeness (Part 5)**
        **Validates: Requirements 3.2.1**
        
        Test that get_variables() extracts variables from BOTH title and description.
        """
        title = " ".join([f"{{{var}}}" for var in title_vars])
        description = " ".join([f"{{{var}}}" for var in desc_vars])
        
        expected = set(title_vars) | set(desc_vars)
        
        template = TaskTemplate(
            name="test",
            title=title,
            description=description,
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[TemplatePrompt("dummy", "Dummy question")]
        )
        
        extracted = template.get_variables()
        
        # Should extract from both title and description
        assert extracted == expected, \
            f"get_variables() should extract from both title and description. Expected: {expected}, Got: {extracted}"
    
    @staticmethod
    def valid_template_name():
        """Generate valid template names matching pattern ^[a-zA-Z0-9_-]+$"""
        # Valid characters: letters, digits, underscore, hyphen
        # Must have at least one character
        return st.text(
            alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-',
            min_size=1,
            max_size=50
        )
    
    @staticmethod
    def invalid_template_name():
        """Generate invalid template names that should be rejected"""
        return st.one_of(
            # Empty string
            st.just(""),
            # Whitespace only
            st.text(alphabet=' \t\n', min_size=1, max_size=10),
            # Contains spaces
            st.builds(lambda parts: ' '.join(parts), 
                     st.lists(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=5), min_size=2, max_size=3)),
            # Contains special characters not allowed
            st.builds(lambda name, char: f"{name}{char}", 
                     st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=10),
                     st.sampled_from(['@', '!', '#', '$', '%', '^', '&', '*', '(', ')', '+', '=', '[', ']', '{', '}', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/', '~', '`'])),
            # Unicode characters
            st.text(alphabet='αβγδεζηθικλμνξοπρστυφχψω', min_size=1, max_size=10),
            # Mix of valid and invalid
            st.builds(lambda valid, invalid: f"{valid} {invalid}",
                     st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=5),
                     st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=5))
        )
    
    @given(valid_name=valid_template_name())
    def test_template_name_validation_accepts_valid_names(self, valid_name):
        """
        **Property 5: Template Name Validation**
        **Validates: Requirements 3.5.1**
        
        Test that validation accepts all valid template names.
        
        Valid names must match pattern: ^[a-zA-Z0-9_-]+$
        This includes:
        - Letters (uppercase and lowercase)
        - Digits
        - Underscores
        - Hyphens
        - At least one character
        """
        template = TaskTemplate(
            name=valid_name,
            title="Title {var}",
            description="Description",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[TemplatePrompt("var", "Question?")]
        )
        
        errors = template.validate()
        
        # Should not have name-related validation errors
        name_errors = [err for err in errors if "Invalid name" in err or "name cannot be empty" in err]
        assert len(name_errors) == 0, \
            f"Valid name '{valid_name}' should pass validation but got errors: {name_errors}"
    
    @given(invalid_name=invalid_template_name())
    def test_template_name_validation_rejects_invalid_names(self, invalid_name):
        """
        **Property 5: Template Name Validation**
        **Validates: Requirements 3.5.1**
        
        Test that validation rejects all invalid template names.
        
        Invalid names include:
        - Empty strings
        - Whitespace-only strings
        - Names with spaces
        - Names with special characters not in [a-zA-Z0-9_-]
        - Unicode characters
        """
        template = TaskTemplate(
            name=invalid_name,
            title="Title {var}",
            description="Description",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[TemplatePrompt("var", "Question?")]
        )
        
        errors = template.validate()
        
        # Should have name-related validation errors
        name_errors = [err for err in errors if "Invalid name" in err or "name cannot be empty" in err]
        assert len(name_errors) > 0, \
            f"Invalid name '{invalid_name}' should be rejected but validation passed"
    
    @given(
        valid_name=valid_template_name(),
        text_before=st.text(max_size=20),
        text_after=st.text(max_size=20)
    )
    def test_template_name_validation_boundary_cases(self, valid_name, text_before, text_after):
        """
        **Property 5: Template Name Validation**
        **Validates: Requirements 3.5.1**
        
        Test that validation properly handles boundary cases.
        
        The pattern ^[a-zA-Z0-9_-]+$ should match the ENTIRE string,
        not just a substring. Names with valid characters surrounded
        by invalid characters should be rejected.
        """
        # Create names with valid core but invalid wrapper
        # Only test if the wrapper actually adds invalid characters
        if text_before.strip() or text_after.strip():
            wrapped_name = f"{text_before}{valid_name}{text_after}"
            
            # If the wrapped name is different from valid_name, it should be rejected
            if wrapped_name != valid_name:
                template = TaskTemplate(
                    name=wrapped_name,
                    title="Title {var}",
                    description="Description",
                    priority=Priority.REQUIRED,
                    estimated_effort=3,
                    prompts=[TemplatePrompt("var", "Question?")]
                )
                
                errors = template.validate()
                
                # Check if the wrapped name matches the valid pattern
                pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
                if pattern.match(wrapped_name):
                    # If it matches, it should pass validation
                    name_errors = [err for err in errors if "Invalid name" in err or "name cannot be empty" in err]
                    assert len(name_errors) == 0, \
                        f"Name '{wrapped_name}' matches pattern but validation failed"
                else:
                    # If it doesn't match, it should fail validation
                    name_errors = [err for err in errors if "Invalid name" in err or "name cannot be empty" in err]
                    assert len(name_errors) > 0, \
                        f"Name '{wrapped_name}' doesn't match pattern but validation passed"
    
    @given(
        name=valid_template_name(),
        title=st.text(min_size=1, max_size=200),
        description=st.text(min_size=1, max_size=500),
        priority=st.sampled_from([Priority.REQUIRED, Priority.RECOMMENDED, Priority.OPTIONAL]),
        estimated_effort=st.integers(min_value=1, max_value=5),
        prompts=st.lists(
            st.builds(
                TemplatePrompt,
                key=valid_identifier(),
                question=st.text(min_size=1, max_size=100),
                required=st.booleans(),
                multiline=st.booleans(),
                default=st.one_of(st.none(), st.text(max_size=50))
            ),
            min_size=1,
            max_size=10,
            unique_by=lambda p: p.key
        ),
        acceptance_criteria=st.lists(st.text(min_size=1, max_size=100), max_size=10)
    )
    def test_serialization_round_trip_preserves_template_equivalence(
        self, name, title, description, priority, estimated_effort, prompts, acceptance_criteria
    ):
        """
        **Property 4: Template Serialization Round-Trip**
        **Validates: Requirements 3.2.4**
        
        Test that to_dict() → from_dict() preserves template equivalence.
        
        For any valid TaskTemplate object, serializing to dictionary via to_dict()
        and then deserializing via from_dict() should produce a template equivalent
        to the original.
        
        This property ensures that:
        1. No data is lost during serialization
        2. Deserialization correctly reconstructs the object
        3. The template can be safely persisted and loaded
        """
        # Create TaskTemplate from generated parameters
        template = TaskTemplate(
            name=name,
            title=title,
            description=description,
            priority=priority,
            estimated_effort=estimated_effort,
            prompts=prompts,
            acceptance_criteria=acceptance_criteria
        )
        
        # Serialize to dictionary
        serialized = template.to_dict()
        
        # Deserialize back to TaskTemplate
        restored = TaskTemplate.from_dict(serialized)
        
        # Verify all fields are preserved
        assert restored.name == template.name, \
            f"Name not preserved: expected '{template.name}', got '{restored.name}'"
        
        assert restored.title == template.title, \
            f"Title not preserved: expected '{template.title}', got '{restored.title}'"
        
        assert restored.description == template.description, \
            f"Description not preserved: expected '{template.description}', got '{restored.description}'"
        
        assert restored.priority == template.priority, \
            f"Priority not preserved: expected {template.priority}, got {restored.priority}"
        
        assert restored.estimated_effort == template.estimated_effort, \
            f"Estimated effort not preserved: expected {template.estimated_effort}, got {restored.estimated_effort}"
        
        assert restored.acceptance_criteria == template.acceptance_criteria, \
            f"Acceptance criteria not preserved: expected {template.acceptance_criteria}, got {restored.acceptance_criteria}"
        
        # Verify prompts are preserved
        assert len(restored.prompts) == len(template.prompts), \
            f"Number of prompts not preserved: expected {len(template.prompts)}, got {len(restored.prompts)}"
        
        for i, (original_prompt, restored_prompt) in enumerate(zip(template.prompts, restored.prompts)):
            assert restored_prompt.key == original_prompt.key, \
                f"Prompt[{i}] key not preserved: expected '{original_prompt.key}', got '{restored_prompt.key}'"
            
            assert restored_prompt.question == original_prompt.question, \
                f"Prompt[{i}] question not preserved: expected '{original_prompt.question}', got '{restored_prompt.question}'"
            
            assert restored_prompt.required == original_prompt.required, \
                f"Prompt[{i}] required not preserved: expected {original_prompt.required}, got {restored_prompt.required}"
            
            assert restored_prompt.multiline == original_prompt.multiline, \
                f"Prompt[{i}] multiline not preserved: expected {original_prompt.multiline}, got {restored_prompt.multiline}"
            
            assert restored_prompt.default == original_prompt.default, \
                f"Prompt[{i}] default not preserved: expected '{original_prompt.default}', got '{restored_prompt.default}'"
        
        # Verify that get_variables() returns the same result
        assert restored.get_variables() == template.get_variables(), \
            f"get_variables() not consistent after round-trip: expected {template.get_variables()}, got {restored.get_variables()}"
        
        # Verify that validation produces the same result
        original_errors = template.validate()
        restored_errors = restored.validate()
        assert set(original_errors) == set(restored_errors), \
            f"Validation results differ after round-trip: original={original_errors}, restored={restored_errors}"
    
    @given(
        name=valid_template_name(),
        title=st.text(min_size=1, max_size=100),
        description=st.text(min_size=1, max_size=200),
        priority=st.sampled_from([Priority.REQUIRED, Priority.RECOMMENDED, Priority.OPTIONAL]),
        estimated_effort=st.integers(min_value=1, max_value=5),
        prompts=st.lists(
            st.builds(
                TemplatePrompt,
                key=valid_identifier(),
                question=st.text(min_size=1, max_size=100),
                required=st.booleans(),
                multiline=st.booleans(),
                default=st.one_of(st.none(), st.text(max_size=50))
            ),
            min_size=1,
            max_size=10,
            unique_by=lambda p: p.key
        )
    )
    def test_template_field_type_validation(self, name, title, description, priority, estimated_effort, prompts):
        """
        **Property 6: Template Field Type Validation**
        **Validates: Requirements 3.5.2**
        
        Test that validation ensures priority is valid, effort range is [1,5], and prompts non-empty.
        
        For any template data, validation SHALL ensure:
        - priority is a valid Priority enum value
        - estimated_effort is an integer in range [1,5]
        - prompts is a non-empty list
        
        This property validates the basic field type constraints that ensure
        template data integrity.
        """
        template = TaskTemplate(
            name=name,
            title=title,
            description=description,
            priority=priority,
            estimated_effort=estimated_effort,
            prompts=prompts,
            acceptance_criteria=[]
        )
        
        errors = template.validate()
        
        # Priority should be valid (since we're using valid enum values)
        # Look for actual priority validation errors, not warnings about prompts
        priority_errors = [err for err in errors if "priority" in err.lower() and "prompt" not in err.lower()]
        assert len(priority_errors) == 0, \
            f"Valid priority {priority} should not produce errors: {priority_errors}"
        
        # Effort should be valid (since we're generating 1-5)
        effort_errors = [err for err in errors if "estimated effort must be" in err.lower()]
        assert len(effort_errors) == 0, \
            f"Valid effort {estimated_effort} should not produce errors: {effort_errors}"
        
        # Prompts should be valid (since we're generating non-empty list)
        prompts_empty_errors = [err for err in errors if "must have at least one prompt" in err]
        assert len(prompts_empty_errors) == 0, \
            f"Non-empty prompts list should not produce empty prompts error: {prompts_empty_errors}"
    
    @given(
        invalid_effort=st.one_of(
            st.integers(max_value=0),  # Below range
            st.integers(min_value=6)   # Above range
        )
    )
    def test_template_field_type_validation_invalid_effort(self, invalid_effort):
        """
        **Property 6: Template Field Type Validation**
        **Validates: Requirements 3.5.2**
        
        Test that validation rejects invalid estimated_effort values outside [1,5].
        """
        template = TaskTemplate(
            name="test",
            title="Test",
            description="Test description",
            priority=Priority.REQUIRED,
            estimated_effort=invalid_effort,
            prompts=[TemplatePrompt("var", "Question?")],
            acceptance_criteria=[]
        )
        
        errors = template.validate()
        
        # Should have effort-related validation error
        effort_errors = [err for err in errors if "effort" in err.lower() and "1-5" in err]
        assert len(effort_errors) > 0, \
            f"Invalid effort {invalid_effort} should be rejected but validation passed"
    
    def test_template_field_type_validation_empty_prompts(self):
        """
        **Property 6: Template Field Type Validation**
        **Validates: Requirements 3.5.2**
        
        Test that validation rejects templates with empty prompts list.
        """
        template = TaskTemplate(
            name="test",
            title="Test",
            description="Test description",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[],  # Empty prompts list
            acceptance_criteria=[]
        )
        
        errors = template.validate()
        
        # Should have prompts-related validation error
        prompts_errors = [err for err in errors if "must have at least one prompt" in err]
        assert len(prompts_errors) > 0, \
            f"Empty prompts list should be rejected but validation passed"
    
    @given(
        variables_in_template=st.lists(valid_identifier(), min_size=1, max_size=5, unique=True),
        extra_prompts=st.lists(valid_identifier(), min_size=0, max_size=3, unique=True)
    )
    def test_variable_prompt_consistency_valid(self, variables_in_template, extra_prompts):
        """
        **Property 7: Variable-Prompt Consistency**
        **Validates: Requirements 3.5.3**
        
        Test that validation succeeds when all template variables are defined in prompts.
        
        For any template, validation SHALL ensure that the set of variables in the
        template text is a subset of (or equal to) the set of prompt keys defined
        in the prompts list.
        
        Having extra prompts (not used in template) is allowed and generates a warning,
        but having undefined variables (used in template but not in prompts) is an error.
        """
        # Build template with variables
        title = "Task: " + " ".join([f"{{{var}}}" for var in variables_in_template[:2]]) if len(variables_in_template) >= 2 else f"{{{variables_in_template[0]}}}"
        description = "Description: " + " ".join([f"{{{var}}}" for var in variables_in_template])
        
        # Create prompts for all variables + extra prompts
        all_prompt_keys = list(variables_in_template) + list(extra_prompts)
        prompts = [TemplatePrompt(key, f"Question for {key}?") for key in all_prompt_keys]
        
        template = TaskTemplate(
            name="test",
            title=title,
            description=description,
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=prompts,
            acceptance_criteria=[]
        )
        
        errors = template.validate()
        
        # Should NOT have undefined variable errors
        undefined_errors = [err for err in errors if "not defined in prompts" in err]
        assert len(undefined_errors) == 0, \
            f"All variables are defined in prompts, should not have undefined errors: {undefined_errors}"
        
        # Extract variables using get_variables()
        extracted_vars = template.get_variables()
        prompt_keys = {p.key for p in prompts}
        
        # All extracted variables should be in prompt keys
        assert extracted_vars.issubset(prompt_keys), \
            f"Variables {extracted_vars} should be subset of prompt keys {prompt_keys}"
    
    @given(
        defined_variables=st.lists(valid_identifier(), min_size=1, max_size=3, unique=True),
        undefined_variables=st.lists(valid_identifier(), min_size=1, max_size=3, unique=True)
    )
    def test_variable_prompt_consistency_invalid(self, defined_variables, undefined_variables):
        """
        **Property 7: Variable-Prompt Consistency**
        **Validates: Requirements 3.5.3**
        
        Test that validation fails when template contains variables not defined in prompts.
        """
        # Ensure undefined variables are actually different from defined ones
        undefined_variables = [v for v in undefined_variables if v not in defined_variables]
        
        if not undefined_variables:
            # Skip if all "undefined" variables are in defined list
            return
        
        # Build template with both defined and undefined variables
        all_vars = defined_variables + undefined_variables
        title = f"Task: {{{all_vars[0]}}}"
        description = "Description: " + " ".join([f"{{{var}}}" for var in all_vars])
        
        # Create prompts only for defined variables
        prompts = [TemplatePrompt(key, f"Question for {key}?") for key in defined_variables]
        
        template = TaskTemplate(
            name="test",
            title=title,
            description=description,
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=prompts,
            acceptance_criteria=[]
        )
        
        errors = template.validate()
        
        # Should have undefined variable errors
        undefined_errors = [err for err in errors if "not defined in prompts" in err]
        assert len(undefined_errors) > 0, \
            f"Template has undefined variables {undefined_variables}, should fail validation but passed"
        
        # Verify that the error mentions the undefined variables
        error_text = " ".join(undefined_errors)
        for undef_var in undefined_variables:
            assert undef_var in error_text, \
                f"Error should mention undefined variable '{undef_var}': {error_text}"



class TestTemplateEngine:
    """Test suite for TemplateEngine class (Task 5.1 and 5.2)"""
    
    def test_replace_variables_simple_replacement(self):
        """Test that _replace_variables() replaces single variable correctly"""
        # Create mock template_store and task_store
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        text = "Implement {feature_name} feature"
        variables = {"feature_name": "authentication"}
        
        result = engine._replace_variables(text, variables)
        
        assert result == "Implement authentication feature"
    
    def test_replace_variables_multiple_variables(self):
        """Test that _replace_variables() replaces multiple variables correctly"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        text = "Add {feature} to {component} module"
        variables = {
            "feature": "caching",
            "component": "database"
        }
        
        result = engine._replace_variables(text, variables)
        
        assert result == "Add caching to database module"
    
    def test_replace_variables_duplicate_occurrences(self):
        """Test that _replace_variables() replaces all occurrences of a variable"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        text = "The {feature} is great. Use {feature} wisely. {feature} rocks!"
        variables = {"feature": "template"}
        
        result = engine._replace_variables(text, variables)
        
        assert result == "The template is great. Use template wisely. template rocks!"
        assert "{feature}" not in result
    
    def test_replace_variables_empty_variables_dict(self):
        """Test that _replace_variables() handles empty variables dict"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        text = "No variables here"
        variables = {}
        
        result = engine._replace_variables(text, variables)
        
        assert result == "No variables here"
    
    def test_replace_variables_text_with_no_placeholders(self):
        """Test that _replace_variables() handles text with no placeholders"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        text = "Simple text without any placeholders"
        variables = {"feature": "test"}
        
        result = engine._replace_variables(text, variables)
        
        assert result == "Simple text without any placeholders"
    
    def test_replace_variables_leaves_unreplaced_placeholders(self):
        """Test that _replace_variables() leaves placeholders for which no value is provided"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        text = "Add {feature} to {component}"
        variables = {"feature": "logging"}  # component not provided
        
        result = engine._replace_variables(text, variables)
        
        assert result == "Add logging to {component}"
        assert "{feature}" not in result
        assert "{component}" in result
    
    def test_replace_variables_with_multiline_text(self):
        """Test that _replace_variables() works with multiline text"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        text = """### Feature: {feature_name}
        
Description: {description}

Implementation steps:
- Design {feature_name}
- Implement {feature_name}
- Test {feature_name}"""
        
        variables = {
            "feature_name": "user authentication",
            "description": "JWT-based auth system"
        }
        
        result = engine._replace_variables(text, variables)
        
        assert "user authentication" in result
        assert "JWT-based auth system" in result
        assert "{feature_name}" not in result
        assert "{description}" not in result
    
    def test_replace_variables_with_special_characters_in_values(self):
        """Test that _replace_variables() handles special characters in replacement values"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        text = "Fix bug: {bug_description}"
        variables = {"bug_description": "Error: {status=500} & response=null"}
        
        result = engine._replace_variables(text, variables)
        
        assert result == "Fix bug: Error: {status=500} & response=null"
    
    def test_replace_variables_empty_string_value(self):
        """Test that _replace_variables() handles empty string as replacement value"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        text = "Prefix{separator}Suffix"
        variables = {"separator": ""}
        
        result = engine._replace_variables(text, variables)
        
        assert result == "PrefixSuffix"
    
    def test_replace_variables_with_unicode_characters(self):
        """Test that _replace_variables() handles unicode characters correctly"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        text = "实现 {feature_name} 功能"
        variables = {"feature_name": "用户认证"}
        
        result = engine._replace_variables(text, variables)
        
        assert result == "实现 用户认证 功能"
    
    def test_validate_required_variables_all_required_provided(self):
        """Test that _validate_required_variables() succeeds when all required variables are provided"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        # Create template with required and optional prompts
        template = TaskTemplate(
            name="test",
            title="Test {required1}",
            description="{required2} and {optional1}",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("required1", "Enter value 1", required=True),
                TemplatePrompt("required2", "Enter value 2", required=True),
                TemplatePrompt("optional1", "Enter optional", required=False)
            ]
        )
        
        # Provide all required variables
        variables = {
            "required1": "value1",
            "required2": "value2"
        }
        
        # Should not raise any exception
        engine._validate_required_variables(template, variables)
    
    def test_validate_required_variables_missing_single_required(self):
        """Test that _validate_required_variables() raises MissingVariableError for missing required variable"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        template = TaskTemplate(
            name="test",
            title="Test {required1}",
            description="{required2}",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("required1", "Enter value 1", required=True),
                TemplatePrompt("required2", "Enter value 2", required=True)
            ]
        )
        
        # Only provide one required variable
        variables = {"required1": "value1"}
        
        with pytest.raises(MissingVariableError) as exc_info:
            engine._validate_required_variables(template, variables)
        
        assert "required2" in str(exc_info.value)
        assert "Missing required variables" in str(exc_info.value)
    
    def test_validate_required_variables_missing_multiple_required(self):
        """Test that _validate_required_variables() raises MissingVariableError for multiple missing variables"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        template = TaskTemplate(
            name="test",
            title="Test {required1}",
            description="{required2} and {required3}",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("required1", "Enter value 1", required=True),
                TemplatePrompt("required2", "Enter value 2", required=True),
                TemplatePrompt("required3", "Enter value 3", required=True)
            ]
        )
        
        # Provide no variables
        variables = {}
        
        with pytest.raises(MissingVariableError) as exc_info:
            engine._validate_required_variables(template, variables)
        
        error_message = str(exc_info.value)
        assert "Missing required variables" in error_message
        # All three required variables should be in the error message
        assert "required1" in error_message or "required2" in error_message or "required3" in error_message
    
    def test_validate_required_variables_optional_not_provided(self):
        """Test that _validate_required_variables() allows missing optional variables"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        template = TaskTemplate(
            name="test",
            title="Test {required1}",
            description="{optional1} and {optional2}",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("required1", "Enter value 1", required=True),
                TemplatePrompt("optional1", "Enter optional 1", required=False),
                TemplatePrompt("optional2", "Enter optional 2", required=False)
            ]
        )
        
        # Only provide required variable, omit optional ones
        variables = {"required1": "value1"}
        
        # Should not raise any exception
        engine._validate_required_variables(template, variables)
    
    def test_validate_required_variables_empty_dict(self):
        """Test that _validate_required_variables() raises error when variables dict is empty"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        template = TaskTemplate(
            name="test",
            title="Test {required1}",
            description="{required2}",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("required1", "Enter value 1", required=True),
                TemplatePrompt("required2", "Enter value 2", required=True)
            ]
        )
        
        # Empty variables dict
        variables = {}
        
        with pytest.raises(MissingVariableError):
            engine._validate_required_variables(template, variables)
    
    def test_validate_required_variables_all_optional_no_variables_provided(self):
        """Test that _validate_required_variables() succeeds when all prompts are optional"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        template = TaskTemplate(
            name="test",
            title="Test {optional1}",
            description="{optional2}",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("optional1", "Enter optional 1", required=False),
                TemplatePrompt("optional2", "Enter optional 2", required=False)
            ]
        )
        
        # No variables provided
        variables = {}
        
        # Should not raise any exception since all prompts are optional
        engine._validate_required_variables(template, variables)
    
    def test_validate_required_variables_extra_variables_provided(self):
        """Test that _validate_required_variables() allows extra variables beyond required"""
        template_store = Mock()
        task_store = Mock()
        
        engine = TemplateEngine(template_store, task_store)
        
        template = TaskTemplate(
            name="test",
            title="Test {required1}",
            description="{required2}",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("required1", "Enter value 1", required=True),
                TemplatePrompt("required2", "Enter value 2", required=True)
            ]
        )
        
        # Provide required variables plus extra ones
        variables = {
            "required1": "value1",
            "required2": "value2",
            "extra_var": "extra_value"
        }
        
        # Should not raise any exception
        engine._validate_required_variables(template, variables)


# ===== Tests for create_task_from_template() method (Task 5.7) =====

class TestCreateTaskFromTemplate:
    """Test suite for TemplateEngine.create_task_from_template() method"""
    
    def test_create_task_from_template_raises_if_template_not_found(self):
        """Test that create_task_from_template raises TemplateNotFoundError when template doesn't exist"""
        from harness.templates import TemplateNotFoundError
        
        template_store = Mock()
        task_store = Mock()
        
        # Mock template_store.get_template() to return None
        template_store.get_template.return_value = None
        
        engine = TemplateEngine(template_store, task_store)
        
        with pytest.raises(TemplateNotFoundError) as exc_info:
            engine.create_task_from_template("nonexistent", interactive=False)
        
        assert "nonexistent" in str(exc_info.value)
        template_store.get_template.assert_called_once_with("nonexistent")
    
    def test_create_task_from_template_raises_if_template_invalid(self):
        """Test that create_task_from_template raises TemplateValidationError for invalid template"""
        from harness.templates import TemplateValidationError
        
        template_store = Mock()
        task_store = Mock()
        
        # Create an invalid template (empty prompts list)
        invalid_template = TaskTemplate(
            name="invalid",
            title="Test",
            description="Test",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[]  # Invalid: must have at least one prompt
        )
        
        template_store.get_template.return_value = invalid_template
        
        engine = TemplateEngine(template_store, task_store)
        
        with pytest.raises(TemplateValidationError):
            engine.create_task_from_template("invalid", interactive=False)
    
    def test_create_task_from_template_non_interactive_success(self):
        """Test create_task_from_template in non-interactive mode with valid variables"""
        from harness.models import Task
        
        template_store = Mock()
        task_store = Mock()
        
        # Create a valid template
        template = TaskTemplate(
            name="feature",
            title="Implement {feature_name} feature",
            description="Add {feature_name} with {component} component",
            priority=Priority.RECOMMENDED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("feature_name", "Feature name?", required=True),
                TemplatePrompt("component", "Component?", required=True)
            ],
            acceptance_criteria=["Feature works", "Tests pass"]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 42
        
        engine = TemplateEngine(template_store, task_store)
        
        # Provide variables
        variables = {
            "feature_name": "authentication",
            "component": "UserService"
        }
        
        task = engine.create_task_from_template(
            "feature",
            variables=variables,
            interactive=False
        )
        
        # Verify task was created correctly
        assert isinstance(task, Task)
        assert task.id == 42
        assert task.title == "Implement authentication feature"
        assert task.description == "Add authentication with UserService component"
        assert task.priority == Priority.RECOMMENDED
        assert task.estimated_effort == 3
        assert task.acceptance_criteria == ["Feature works", "Tests pass"]
        
        # Verify methods were called
        template_store.get_template.assert_called_once_with("feature")
        task_store.get_next_task_id.assert_called_once()
    
    def test_create_task_from_template_non_interactive_missing_required_variable(self):
        """Test that create_task_from_template raises MissingVariableError for missing required variables"""
        template_store = Mock()
        task_store = Mock()
        
        template = TaskTemplate(
            name="bugfix",
            title="Fix {bug_name}",
            description="Fix bug: {bug_description}",
            priority=Priority.REQUIRED,
            estimated_effort=2,
            prompts=[
                TemplatePrompt("bug_name", "Bug name?", required=True),
                TemplatePrompt("bug_description", "Description?", required=True)
            ]
        )
        
        template_store.get_template.return_value = template
        
        engine = TemplateEngine(template_store, task_store)
        
        # Only provide one required variable
        variables = {
            "bug_name": "login-failure"
            # Missing: bug_description
        }
        
        with pytest.raises(MissingVariableError) as exc_info:
            engine.create_task_from_template(
                "bugfix",
                variables=variables,
                interactive=False
            )
        
        assert "bug_description" in str(exc_info.value)
    
    def test_create_task_from_template_non_interactive_with_optional_variables(self):
        """Test create_task_from_template handles optional variables correctly"""
        from harness.models import Task
        
        template_store = Mock()
        task_store = Mock()
        
        template = TaskTemplate(
            name="refactor",
            title="Refactor {module}",
            description="Refactor {module} - {notes}",
            priority=Priority.OPTIONAL,
            estimated_effort=2,
            prompts=[
                TemplatePrompt("module", "Module?", required=True),
                TemplatePrompt("notes", "Notes?", required=False, default="No notes")
            ]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 10
        
        engine = TemplateEngine(template_store, task_store)
        
        # Only provide required variable
        variables = {
            "module": "auth_service"
        }
        
        task = engine.create_task_from_template(
            "refactor",
            variables=variables,
            interactive=False
        )
        
        assert task.id == 10
        assert task.title == "Refactor auth_service"
        # Optional variable not provided, so {notes} remains unreplaced
        assert task.description == "Refactor auth_service - {notes}"
    
    def test_create_task_from_template_non_interactive_empty_variables_dict(self):
        """Test create_task_from_template with empty variables dict raises error for required variables"""
        template_store = Mock()
        task_store = Mock()
        
        template = TaskTemplate(
            name="test",
            title="Test {var}",
            description="Test",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("var", "Var?", required=True)
            ]
        )
        
        template_store.get_template.return_value = template
        
        engine = TemplateEngine(template_store, task_store)
        
        with pytest.raises(MissingVariableError):
            engine.create_task_from_template("test", variables={}, interactive=False)
    
    def test_create_task_from_template_non_interactive_none_variables(self):
        """Test create_task_from_template with None variables raises error for required variables"""
        template_store = Mock()
        task_store = Mock()
        
        template = TaskTemplate(
            name="test",
            title="Test {var}",
            description="Test",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("var", "Var?", required=True)
            ]
        )
        
        template_store.get_template.return_value = template
        
        engine = TemplateEngine(template_store, task_store)
        
        with pytest.raises(MissingVariableError):
            engine.create_task_from_template("test", variables=None, interactive=False)
    
    def test_create_task_from_template_copies_acceptance_criteria(self):
        """Test that create_task_from_template copies acceptance_criteria from template"""
        from harness.models import Task
        
        template_store = Mock()
        task_store = Mock()
        
        template = TaskTemplate(
            name="test",
            title="Test {var}",
            description="Test",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("var", "Var?", required=True)
            ],
            acceptance_criteria=["Criterion 1", "Criterion 2", "Criterion 3"]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 1
        
        engine = TemplateEngine(template_store, task_store)
        
        task = engine.create_task_from_template(
            "test",
            variables={"var": "value"},
            interactive=False
        )
        
        assert task.acceptance_criteria == ["Criterion 1", "Criterion 2", "Criterion 3"]
        
        # Verify it's a copy (modifying task shouldn't affect template)
        task.acceptance_criteria.append("New criterion")
        assert len(template.acceptance_criteria) == 3  # Original unchanged
    
    def test_create_task_from_template_replaces_multiple_occurrences(self):
        """Test that variable replacement handles multiple occurrences of same variable"""
        from harness.models import Task
        
        template_store = Mock()
        task_store = Mock()
        
        template = TaskTemplate(
            name="test",
            title="{feature} - {feature} Implementation",
            description="Implement {feature} and test {feature} thoroughly. {feature} is important.",
            priority=Priority.REQUIRED,
            estimated_effort=4,
            prompts=[
                TemplatePrompt("feature", "Feature?", required=True)
            ]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 5
        
        engine = TemplateEngine(template_store, task_store)
        
        task = engine.create_task_from_template(
            "test",
            variables={"feature": "Dashboard"},
            interactive=False
        )
        
        assert task.title == "Dashboard - Dashboard Implementation"
        assert task.description == "Implement Dashboard and test Dashboard thoroughly. Dashboard is important."
    
    def test_create_task_from_template_preserves_task_status_default(self):
        """Test that created task has default TODO status"""
        from harness.models import Task, TaskStatus
        
        template_store = Mock()
        task_store = Mock()
        
        template = TaskTemplate(
            name="test",
            title="Test {var}",
            description="Test description",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("var", "Var?", required=False)
            ]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 1
        
        engine = TemplateEngine(template_store, task_store)
        
        task = engine.create_task_from_template("test", variables={}, interactive=False)
        
        # Task should have default TODO status
        assert task.status == TaskStatus.TODO
    
    def test_create_task_from_template_with_extra_variables(self):
        """Test that extra variables (not in template) don't cause issues"""
        from harness.models import Task
        
        template_store = Mock()
        task_store = Mock()
        
        template = TaskTemplate(
            name="test",
            title="Test {var1}",
            description="Test",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("var1", "Var1?", required=True)
            ]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 1
        
        engine = TemplateEngine(template_store, task_store)
        
        # Provide extra variables that aren't in the template
        variables = {
            "var1": "value1",
            "var2": "value2",  # Extra
            "var3": "value3"   # Extra
        }
        
        task = engine.create_task_from_template("test", variables=variables, interactive=False)
        
        assert task.title == "Test value1"
        # Extra variables should be ignored (not cause errors)


# ===== Integration Tests for Interactive Mode (Task 5.8) =====

class TestTemplateEngineInteractiveMode:
    """Integration tests for TemplateEngine interactive mode with mocked user input"""
    
    def test_interactive_mode_with_single_line_inputs(self, monkeypatch):
        """Test interactive mode with single-line inputs using click.prompt"""
        from harness.models import Task
        from unittest.mock import patch
        
        template_store = Mock()
        task_store = Mock()
        
        # Create template with single-line prompts
        template = TaskTemplate(
            name="feature",
            title="Implement {feature_name} feature",
            description="Add {feature_name} to {component}",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("feature_name", "请输入功能名称", required=True, multiline=False),
                TemplatePrompt("component", "请输入组件名称", required=True, multiline=False)
            ],
            acceptance_criteria=["Feature works", "Tests pass"]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 1
        
        engine = TemplateEngine(template_store, task_store)
        
        # Mock click.prompt and click.echo
        prompt_responses = ["用户认证", "AuthService"]
        prompt_call_count = [0]
        
        def mock_prompt(question, default=None, show_default=False):
            response = prompt_responses[prompt_call_count[0]]
            prompt_call_count[0] += 1
            return response
        
        with patch('click.prompt', side_effect=mock_prompt) as mock_click_prompt, \
             patch('click.echo') as mock_echo:
            
            task = engine.create_task_from_template("feature", interactive=True)
            
            # Verify task was created correctly
            assert task.title == "Implement 用户认证 feature"
            assert task.description == "Add 用户认证 to AuthService"
            assert task.priority == Priority.REQUIRED
            assert task.estimated_effort == 3
            
            # Verify click.echo was called to display template name
            assert mock_echo.call_count >= 1
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            assert any("feature" in str(call) for call in echo_calls)
            
            # Verify click.prompt was called twice
            assert mock_click_prompt.call_count == 2
    
    def test_interactive_mode_with_multiline_input(self, monkeypatch):
        """Test interactive mode with multiline input using input() and EOFError"""
        from harness.models import Task
        from unittest.mock import patch
        
        template_store = Mock()
        task_store = Mock()
        
        # Create template with multiline prompt
        template = TaskTemplate(
            name="bugfix",
            title="Fix {bug_name}",
            description="Bug: {bug_description}",
            priority=Priority.REQUIRED,
            estimated_effort=2,
            prompts=[
                TemplatePrompt("bug_name", "请输入Bug名称", required=True, multiline=False),
                TemplatePrompt("bug_description", "请输入Bug描述", required=True, multiline=True)
            ]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 2
        
        engine = TemplateEngine(template_store, task_store)
        
        # Mock inputs
        # For multiline input, input() is called multiple times until EOFError
        multiline_inputs = [
            "登录接口返回500错误",
            "复现步骤:",
            "1. 访问/login",
            "2. 输入用户名密码",
        ]
        input_call_count = [0]
        
        def mock_input(prompt=""):
            if input_call_count[0] < len(multiline_inputs):
                response = multiline_inputs[input_call_count[0]]
                input_call_count[0] += 1
                return response
            else:
                # Simulate Ctrl+D (EOF)
                raise EOFError()
        
        def mock_click_prompt(question, default=None, show_default=False):
            return "登录500错误"
        
        with patch('click.prompt', side_effect=mock_click_prompt), \
             patch('click.echo'), \
             patch('builtins.input', side_effect=mock_input):
            
            task = engine.create_task_from_template("bugfix", interactive=True)
            
            # Verify task was created correctly
            assert task.title == "Fix 登录500错误"
            expected_description = "Bug: " + "\n".join(multiline_inputs)
            assert task.description == expected_description
    
    def test_interactive_mode_with_default_values(self, monkeypatch):
        """Test interactive mode with default values for prompts"""
        from harness.models import Task
        from unittest.mock import patch
        
        template_store = Mock()
        task_store = Mock()
        
        # Create template with prompts that have default values
        template = TaskTemplate(
            name="refactor",
            title="Refactor {module}",
            description="Refactor {module} - Reason: {reason}",
            priority=Priority.RECOMMENDED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("module", "请输入模块名称", required=True, multiline=False),
                TemplatePrompt("reason", "请输入重构原因", required=False, multiline=False, default="提升代码质量")
            ]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 3
        
        engine = TemplateEngine(template_store, task_store)
        
        # Mock click.prompt
        # First call returns module name, second call returns default value
        prompt_responses = ["executor模块", "提升代码质量"]  # User accepts default
        prompt_call_count = [0]
        
        def mock_prompt(question, default=None, show_default=False):
            response = prompt_responses[prompt_call_count[0]]
            prompt_call_count[0] += 1
            return response
        
        with patch('click.prompt', side_effect=mock_prompt) as mock_click_prompt, \
             patch('click.echo'):
            
            task = engine.create_task_from_template("refactor", interactive=True)
            
            # Verify task was created correctly
            assert task.title == "Refactor executor模块"
            assert task.description == "Refactor executor模块 - Reason: 提升代码质量"
            
            # Verify click.prompt was called with default parameter for second prompt
            assert mock_click_prompt.call_count == 2
            second_call_kwargs = mock_click_prompt.call_args_list[1][1]
            assert second_call_kwargs.get('default') == "提升代码质量"
            assert second_call_kwargs.get('show_default') is True
    
    def test_interactive_mode_with_mix_of_required_and_optional(self, monkeypatch):
        """Test interactive mode with mix of required and optional fields"""
        from harness.models import Task
        from unittest.mock import patch
        
        template_store = Mock()
        task_store = Mock()
        
        # Create template with mix of required and optional prompts
        template = TaskTemplate(
            name="task",
            title="{title_text}",
            description="{description_text} - Priority: {priority_text} - Notes: {notes}",
            priority=Priority.REQUIRED,
            estimated_effort=2,
            prompts=[
                TemplatePrompt("title_text", "任务标题", required=True, multiline=False),
                TemplatePrompt("description_text", "任务描述", required=True, multiline=False),
                TemplatePrompt("priority_text", "优先级", required=False, multiline=False, default="中"),
                TemplatePrompt("notes", "备注", required=False, multiline=False, default="无")
            ]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 4
        
        engine = TemplateEngine(template_store, task_store)
        
        # Mock click.prompt - provide required fields and accept defaults for optional
        prompt_responses = ["实现API接口", "完成REST API开发", "中", "无"]
        prompt_call_count = [0]
        
        def mock_prompt(question, default=None, show_default=False):
            response = prompt_responses[prompt_call_count[0]]
            prompt_call_count[0] += 1
            return response
        
        with patch('click.prompt', side_effect=mock_prompt), \
             patch('click.echo'):
            
            task = engine.create_task_from_template("task", interactive=True)
            
            assert task.title == "实现API接口"
            assert task.description == "完成REST API开发 - Priority: 中 - Notes: 无"
    
    def test_interactive_mode_empty_required_field_raises_error(self, monkeypatch):
        """Test that empty required field without default raises MissingVariableError"""
        from unittest.mock import patch
        
        template_store = Mock()
        task_store = Mock()
        
        # Create template with required prompt
        template = TaskTemplate(
            name="test",
            title="{required_field}",
            description="Test",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("required_field", "Required field", required=True, multiline=False)
            ]
        )
        
        template_store.get_template.return_value = template
        
        engine = TemplateEngine(template_store, task_store)
        
        # Mock click.prompt to return empty string
        def mock_prompt(question, default=None, show_default=False):
            return "   "  # Whitespace only
        
        with patch('click.prompt', side_effect=mock_prompt), \
             patch('click.echo'):
            
            with pytest.raises(MissingVariableError) as exc_info:
                engine.create_task_from_template("test", interactive=True)
            
            assert "required_field" in str(exc_info.value)
            assert "cannot be empty" in str(exc_info.value)
    
    def test_interactive_mode_optional_field_with_default_uses_default_when_user_accepts(self, monkeypatch):
        """Test that click.prompt with default returns default when user presses Enter"""
        from harness.models import Task
        from unittest.mock import patch
        
        template_store = Mock()
        task_store = Mock()
        
        # Create template with optional prompt that has a default
        template = TaskTemplate(
            name="test",
            title="{title_field}",
            description="{optional_field}",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("title_field", "Title", required=True, multiline=False),
                TemplatePrompt("optional_field", "Optional", required=False, multiline=False, default="默认值")
            ]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 5
        
        engine = TemplateEngine(template_store, task_store)
        
        # Mock click.prompt - simulate user accepting default by returning the default value
        # This is what click.prompt does when user presses Enter without typing anything
        prompt_responses = ["测试标题", "默认值"]  # Second is the default (user pressed Enter)
        prompt_call_count = [0]
        
        def mock_prompt(question, default=None, show_default=False):
            response = prompt_responses[prompt_call_count[0]]
            prompt_call_count[0] += 1
            return response
        
        with patch('click.prompt', side_effect=mock_prompt), \
             patch('click.echo'):
            
            task = engine.create_task_from_template("test", interactive=True)
            
            # Optional field should have the default value
            assert task.title == "测试标题"
            assert task.description == "默认值"
    
    def test_interactive_mode_displays_template_header(self, monkeypatch):
        """Test that interactive mode displays template name header"""
        from unittest.mock import patch
        
        template_store = Mock()
        task_store = Mock()
        
        # Create simple template
        template = TaskTemplate(
            name="feature-template",
            title="{name}",
            description="Description",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("name", "Name?", required=True, multiline=False)
            ]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 1
        
        engine = TemplateEngine(template_store, task_store)
        
        # Mock prompts
        def mock_prompt(question, default=None, show_default=False):
            return "test"
        
        with patch('click.prompt', side_effect=mock_prompt), \
             patch('click.echo') as mock_echo:
            
            engine.create_task_from_template("feature-template", interactive=True)
            
            # Verify click.echo was called with template name
            echo_calls = [str(call) for call in mock_echo.call_args_list]
            # Should display template name in header
            assert any("feature-template" in str(call) for call in echo_calls)
    
    def test_interactive_mode_multiline_with_multiple_eof_lines(self, monkeypatch):
        """Test multiline input with multiple lines followed by EOFError"""
        from harness.models import Task
        from unittest.mock import patch
        
        template_store = Mock()
        task_store = Mock()
        
        # Create template with multiline field
        template = TaskTemplate(
            name="test",
            title="Test",
            description="{multiline_field}",
            priority=Priority.REQUIRED,
            estimated_effort=1,
            prompts=[
                TemplatePrompt("multiline_field", "Enter multiline text", required=True, multiline=True)
            ]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 1
        
        engine = TemplateEngine(template_store, task_store)
        
        # Mock multiline input
        lines = ["Line 1", "Line 2", "Line 3", "Line 4"]
        input_call_count = [0]
        
        def mock_input(prompt=""):
            if input_call_count[0] < len(lines):
                response = lines[input_call_count[0]]
                input_call_count[0] += 1
                return response
            else:
                raise EOFError()
        
        with patch('builtins.input', side_effect=mock_input), \
             patch('click.echo'):
            
            task = engine.create_task_from_template("test", interactive=True)
            
            # Verify multiline content was joined correctly
            expected_description = "\n".join(lines)
            assert task.description == expected_description
    
    def test_interactive_mode_single_and_multiline_mixed(self, monkeypatch):
        """Test interactive mode with both single-line and multiline prompts"""
        from harness.models import Task
        from unittest.mock import patch
        
        template_store = Mock()
        task_store = Mock()
        
        # Create template with both single-line and multiline prompts
        template = TaskTemplate(
            name="mixed",
            title="{single_line}",
            description="Single: {single_line}\nMulti: {multi_line}",
            priority=Priority.REQUIRED,
            estimated_effort=2,
            prompts=[
                TemplatePrompt("single_line", "Single line input", required=True, multiline=False),
                TemplatePrompt("multi_line", "Multi line input", required=True, multiline=True)
            ]
        )
        
        template_store.get_template.return_value = template
        task_store.get_next_task_id.return_value = 1
        
        engine = TemplateEngine(template_store, task_store)
        
        # Mock single-line prompt
        def mock_prompt(question, default=None, show_default=False):
            return "Single Line Value"
        
        # Mock multiline input
        multiline_data = ["Multi Line 1", "Multi Line 2"]
        input_call_count = [0]
        
        def mock_input(prompt=""):
            if input_call_count[0] < len(multiline_data):
                response = multiline_data[input_call_count[0]]
                input_call_count[0] += 1
                return response
            else:
                raise EOFError()
        
        with patch('click.prompt', side_effect=mock_prompt), \
             patch('builtins.input', side_effect=mock_input), \
             patch('click.echo'):
            
            task = engine.create_task_from_template("mixed", interactive=True)
            
            assert task.title == "Single Line Value"
            expected_desc = "Single: Single Line Value\nMulti: Multi Line 1\nMulti Line 2"
            assert task.description == expected_desc
