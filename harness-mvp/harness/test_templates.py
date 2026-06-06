"""Unit tests for template system - Task 1.1 TemplatePrompt and Task 1.2 TaskTemplate tests"""
import pytest
import re
from hypothesis import given, strategies as st
from harness.templates import TemplatePrompt, TaskTemplate, Priority


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
