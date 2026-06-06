"""Unit tests for TemplateStore - Task 3.1 tests"""
import pytest
from pathlib import Path
import tempfile
import shutil
import json

from harness.template_loader import TemplateStore
from harness.models import Priority


class TestTemplateStore:
    """Test suite for TemplateStore class (Task 3.1)"""
    
    def test_initializes_with_harness_dir(self):
        """Test that TemplateStore initializes with harness_dir path"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            assert store.harness_dir == test_dir
            assert store.custom_template_dir == test_dir / "templates"
        finally:
            shutil.rmtree(test_dir)
    
    def test_loads_built_in_templates(self):
        """Test that TemplateStore loads all 3 built-in templates"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            # Should have exactly 3 built-in templates
            assert len(store._built_in_templates) == 3
            assert "feature" in store._built_in_templates
            assert "bugfix" in store._built_in_templates
            assert "refactor" in store._built_in_templates
        finally:
            shutil.rmtree(test_dir)
    
    def test_feature_template_structure(self):
        """Test that feature template has correct structure (Requirement 3.1.1)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            feature = store._built_in_templates["feature"]
            
            # Check basic fields
            assert feature.name == "feature"
            assert "{feature_name}" in feature.title
            assert "{description}" in feature.description
            assert feature.priority == Priority.REQUIRED
            assert feature.estimated_effort == 3
            
            # Check prompts
            assert len(feature.prompts) == 2
            prompt_keys = {p.key for p in feature.prompts}
            assert "feature_name" in prompt_keys
            assert "description" in prompt_keys
            
            # Verify validation passes
            errors = feature.validate()
            assert len(errors) == 0, f"Feature template has validation errors: {errors}"
        finally:
            shutil.rmtree(test_dir)
    
    def test_bugfix_template_structure(self):
        """Test that bugfix template has correct structure (Requirement 3.1.2)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            bugfix = store._built_in_templates["bugfix"]
            
            # Check basic fields
            assert bugfix.name == "bugfix"
            assert "{bug_description}" in bugfix.title
            assert bugfix.priority == Priority.REQUIRED
            assert bugfix.estimated_effort == 2
            
            # Check prompts
            assert len(bugfix.prompts) == 4
            prompt_keys = {p.key for p in bugfix.prompts}
            assert "bug_description" in prompt_keys
            assert "description" in prompt_keys
            assert "reproduction_steps" in prompt_keys
            assert "fix_plan" in prompt_keys
            
            # Check fix_plan has default value
            fix_plan_prompt = next(p for p in bugfix.prompts if p.key == "fix_plan")
            assert fix_plan_prompt.required == False
            assert fix_plan_prompt.default == "待分析"
            
            # Verify validation passes
            errors = bugfix.validate()
            assert len(errors) == 0, f"Bugfix template has validation errors: {errors}"
        finally:
            shutil.rmtree(test_dir)
    
    def test_refactor_template_structure(self):
        """Test that refactor template has correct structure (Requirement 3.1.3)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            refactor = store._built_in_templates["refactor"]
            
            # Check basic fields
            assert refactor.name == "refactor"
            assert "{module_name}" in refactor.title
            assert refactor.priority == Priority.RECOMMENDED
            assert refactor.estimated_effort == 3
            
            # Check prompts
            assert len(refactor.prompts) == 3
            prompt_keys = {p.key for p in refactor.prompts}
            assert "module_name" in prompt_keys
            assert "goal" in prompt_keys
            assert "scope" in prompt_keys
            
            # Verify validation passes
            errors = refactor.validate()
            assert len(errors) == 0, f"Refactor template has validation errors: {errors}"
        finally:
            shutil.rmtree(test_dir)
    
    def test_get_template_returns_built_in_template(self):
        """Test that get_template() retrieves built-in templates"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            feature = store.get_template("feature")
            assert feature is not None
            assert feature.name == "feature"
            
            bugfix = store.get_template("bugfix")
            assert bugfix is not None
            assert bugfix.name == "bugfix"
            
            refactor = store.get_template("refactor")
            assert refactor is not None
            assert refactor.name == "refactor"
        finally:
            shutil.rmtree(test_dir)
    
    def test_get_template_returns_none_for_nonexistent(self):
        """Test that get_template() returns None for non-existent template"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            result = store.get_template("nonexistent")
            assert result is None
        finally:
            shutil.rmtree(test_dir)
    
    def test_get_all_templates_returns_all_built_in(self):
        """Test that get_all_templates() returns all built-in templates"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            templates = store.get_all_templates()
            assert len(templates) >= 3
            assert "feature" in templates
            assert "bugfix" in templates
            assert "refactor" in templates
        finally:
            shutil.rmtree(test_dir)
    
    def test_list_templates_returns_tuples(self):
        """Test that list_templates() returns list of tuples"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            templates = store.list_templates()
            assert len(templates) >= 3
            
            # Check tuple structure (name, template, is_custom)
            for name, template, is_custom in templates:
                assert isinstance(name, str)
                assert template is not None
                assert isinstance(is_custom, bool)
                # Built-in templates should be marked as not custom
                if name in ["feature", "bugfix", "refactor"]:
                    assert is_custom == False
        finally:
            shutil.rmtree(test_dir)
    
    def test_load_custom_templates_returns_empty_when_dir_not_exists(self):
        """Test that load_custom_templates() returns empty dict when directory doesn't exist"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            # Templates directory doesn't exist yet
            custom = store.load_custom_templates()
            assert custom == {}
        finally:
            shutil.rmtree(test_dir)


class TestTemplateStoreUnitTests:
    """Unit tests for TemplateStore (Task 3.5)
    
    Tests cover:
    - Built-in templates are loaded correctly
    - Custom templates override built-in
    - Invalid JSON handling
    - Missing directory handling
    
    Requirements: 3.1, 3.4, 3.5
    """
    
    def test_built_in_templates_loaded_correctly(self):
        """Test built-in templates are loaded correctly (Requirement 3.1)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            # Verify all 3 built-in templates are loaded
            assert len(store._built_in_templates) == 3
            
            # Verify each template is valid
            for name, template in store._built_in_templates.items():
                assert template.name == name
                assert template.validate() == []  # No validation errors
                assert len(template.prompts) > 0
                
            # Verify specific templates exist
            assert "feature" in store._built_in_templates
            assert "bugfix" in store._built_in_templates
            assert "refactor" in store._built_in_templates
            
            # Verify feature template details
            feature = store._built_in_templates["feature"]
            assert feature.priority == Priority.REQUIRED
            assert feature.estimated_effort == 3
            assert len(feature.prompts) == 2
            
        finally:
            shutil.rmtree(test_dir)
    
    def test_custom_templates_override_built_in(self):
        """Test custom templates override built-in templates (Requirement 3.4)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            # Create custom templates directory
            custom_dir = test_dir / "templates"
            custom_dir.mkdir(exist_ok=True)
            
            # Create a custom "feature" template that overrides built-in
            custom_template = {
                "name": "feature",
                "title": "Custom Feature: {name}",
                "description": "Custom description: {description}",
                "priority": "OPTIONAL",
                "estimated_effort": 5,
                "prompts": [
                    {
                        "key": "name",
                        "question": "Custom question",
                        "required": True
                    },
                    {
                        "key": "description",
                        "question": "Custom description question",
                        "required": True
                    }
                ]
            }
            
            # Write custom template to file
            template_file = custom_dir / "feature.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(custom_template, f)
            
            # Get all templates - custom should override built-in
            all_templates = store.get_all_templates()
            
            # Verify the custom template is used
            feature = all_templates["feature"]
            assert feature.title == "Custom Feature: {name}"
            assert feature.priority == Priority.OPTIONAL
            assert feature.estimated_effort == 5
            
            # Verify it's marked as custom in list_templates
            template_list = store.list_templates()
            feature_tuple = next((t for t in template_list if t[0] == "feature"), None)
            assert feature_tuple is not None
            name, template, is_custom = feature_tuple
            assert is_custom == True  # Should be marked as custom
            
        finally:
            shutil.rmtree(test_dir)
    
    def test_invalid_json_handling(self):
        """Test invalid JSON files are handled gracefully (Requirement 3.5)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            # Create custom templates directory
            custom_dir = test_dir / "templates"
            custom_dir.mkdir(exist_ok=True)
            
            # Create invalid JSON file
            invalid_file = custom_dir / "invalid.json"
            with open(invalid_file, 'w', encoding='utf-8') as f:
                f.write("{ invalid json content }")
            
            # Should not raise exception, just log error
            custom = store.load_custom_templates()
            
            # Invalid template should not be loaded
            assert "invalid" not in custom
            
            # Built-in templates should still be accessible
            all_templates = store.get_all_templates()
            assert "feature" in all_templates
            assert "bugfix" in all_templates
            assert "refactor" in all_templates
            
        finally:
            shutil.rmtree(test_dir)
    
    def test_invalid_template_structure_handling(self):
        """Test templates with validation errors are skipped (Requirement 3.5)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            # Create custom templates directory
            custom_dir = test_dir / "templates"
            custom_dir.mkdir(exist_ok=True)
            
            # Create template with validation errors (missing required prompts)
            invalid_template = {
                "name": "invalid",
                "title": "Invalid Template {missing_var}",
                "description": "Description with {undefined_variable}",
                "priority": "REQUIRED",
                "estimated_effort": 3,
                "prompts": [
                    {
                        "key": "wrong_key",
                        "question": "Wrong question",
                        "required": True
                    }
                ]
            }
            
            # Write invalid template to file
            template_file = custom_dir / "invalid.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(invalid_template, f)
            
            # Should not raise exception, just log warning
            custom = store.load_custom_templates()
            
            # Invalid template should not be loaded
            assert "invalid" not in custom
            
            # Built-in templates should still work
            all_templates = store.get_all_templates()
            assert len(all_templates) >= 3
            
        finally:
            shutil.rmtree(test_dir)
    
    def test_missing_directory_handling(self):
        """Test missing custom template directory is handled gracefully (Requirement 3.4)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            # Ensure templates directory doesn't exist
            custom_dir = test_dir / "templates"
            assert not custom_dir.exists()
            
            # Should not raise exception
            custom = store.load_custom_templates()
            assert custom == {}
            
            # get_all_templates should still return built-in templates
            all_templates = store.get_all_templates()
            assert len(all_templates) == 3
            assert "feature" in all_templates
            assert "bugfix" in all_templates
            assert "refactor" in all_templates
            
            # list_templates should still work
            template_list = store.list_templates()
            assert len(template_list) == 3
            
            # All should be marked as not custom
            for name, template, is_custom in template_list:
                assert is_custom == False
            
        finally:
            shutil.rmtree(test_dir)
    
    def test_multiple_custom_templates_loaded(self):
        """Test multiple valid custom templates are loaded correctly (Requirement 3.4)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            # Create custom templates directory
            custom_dir = test_dir / "templates"
            custom_dir.mkdir(exist_ok=True)
            
            # Create multiple custom templates
            templates = [
                {
                    "name": "documentation",
                    "title": "Write {doc_name} documentation",
                    "description": "Content: {content}",
                    "priority": "OPTIONAL",
                    "estimated_effort": 1,
                    "prompts": [
                        {"key": "doc_name", "question": "Doc name?", "required": True},
                        {"key": "content", "question": "Content?", "required": True}
                    ]
                },
                {
                    "name": "api",
                    "title": "Implement {endpoint} API",
                    "description": "Method: {method}",
                    "priority": "REQUIRED",
                    "estimated_effort": 2,
                    "prompts": [
                        {"key": "endpoint", "question": "Endpoint?", "required": True},
                        {"key": "method", "question": "HTTP method?", "required": True}
                    ]
                }
            ]
            
            for template_data in templates:
                template_file = custom_dir / f"{template_data['name']}.json"
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f)
            
            # Load custom templates
            custom = store.load_custom_templates()
            
            # Both custom templates should be loaded
            assert "documentation" in custom
            assert "api" in custom
            
            # get_all_templates should include both custom and built-in
            all_templates = store.get_all_templates()
            assert len(all_templates) == 5  # 3 built-in + 2 custom
            assert "documentation" in all_templates
            assert "api" in all_templates
            assert "feature" in all_templates
            
        finally:
            shutil.rmtree(test_dir)
    
    def test_custom_template_with_empty_prompts_rejected(self):
        """Test custom template with empty prompts list is rejected (Requirement 3.5.2)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            # Create custom templates directory
            custom_dir = test_dir / "templates"
            custom_dir.mkdir(exist_ok=True)
            
            # Create template with empty prompts
            invalid_template = {
                "name": "noprompts",
                "title": "No Prompts Template",
                "description": "Description without variables",
                "priority": "REQUIRED",
                "estimated_effort": 3,
                "prompts": []  # Empty prompts - should fail validation
            }
            
            template_file = custom_dir / "noprompts.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(invalid_template, f)
            
            # Load custom templates
            custom = store.load_custom_templates()
            
            # Template should be rejected due to validation error
            assert "noprompts" not in custom
            
        finally:
            shutil.rmtree(test_dir)
    
    def test_custom_template_with_invalid_effort_rejected(self):
        """Test custom template with invalid effort value is rejected (Requirement 3.5.2)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            # Create custom templates directory
            custom_dir = test_dir / "templates"
            custom_dir.mkdir(exist_ok=True)
            
            # Create template with invalid effort (outside 1-5 range)
            invalid_template = {
                "name": "badeffort",
                "title": "Bad Effort {name}",
                "description": "Description: {desc}",
                "priority": "REQUIRED",
                "estimated_effort": 10,  # Invalid: should be 1-5
                "prompts": [
                    {"key": "name", "question": "Name?", "required": True},
                    {"key": "desc", "question": "Description?", "required": True}
                ]
            }
            
            template_file = custom_dir / "badeffort.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(invalid_template, f)
            
            # Load custom templates
            custom = store.load_custom_templates()
            
            # Template should be rejected due to validation error
            assert "badeffort" not in custom
            
        finally:
            shutil.rmtree(test_dir)
    
    def test_get_template_prioritizes_custom_over_builtin(self):
        """Test get_template() returns custom version when both exist (Requirement 3.4)"""
        test_dir = Path(tempfile.mkdtemp())
        try:
            store = TemplateStore(test_dir)
            
            # Create custom templates directory
            custom_dir = test_dir / "templates"
            custom_dir.mkdir(exist_ok=True)
            
            # Create custom bugfix template
            custom_bugfix = {
                "name": "bugfix",
                "title": "Custom Bugfix: {bug}",
                "description": "Custom fix: {fix}",
                "priority": "OPTIONAL",
                "estimated_effort": 1,
                "prompts": [
                    {"key": "bug", "question": "Bug?", "required": True},
                    {"key": "fix", "question": "Fix?", "required": True}
                ]
            }
            
            template_file = custom_dir / "bugfix.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(custom_bugfix, f)
            
            # Get the bugfix template
            bugfix = store.get_template("bugfix")
            
            # Should be the custom version
            assert bugfix.title == "Custom Bugfix: {bug}"
            assert bugfix.priority == Priority.OPTIONAL
            assert bugfix.estimated_effort == 1
            
        finally:
            shutil.rmtree(test_dir)
