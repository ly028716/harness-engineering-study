"""任务模板加载器 - 管理内置和自定义模板"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from harness.templates import TaskTemplate, TemplatePrompt
from harness.models import Priority

logger = logging.getLogger(__name__)


class TemplateStore:
    """Manages loading and caching of templates
    
    The TemplateStore handles both built-in templates (defined in code)
    and custom templates (loaded from .harness/templates/*.json).
    Custom templates can override built-in templates with the same name.
    """
    
    def __init__(self, harness_dir: Path):
        """Initialize the template store
        
        Args:
            harness_dir: Path to the .harness directory
        """
        self.harness_dir = harness_dir
        self.custom_template_dir = harness_dir / "templates"
        self._cache: Dict[str, TaskTemplate] = {}
        self._built_in_templates: Dict[str, TaskTemplate] = {}
        self._load_built_in_templates()
    
    def _load_built_in_templates(self):
        """Load built-in templates from code
        
        Creates three built-in templates:
        - feature: For implementing new features
        - bugfix: For fixing bugs
        - refactor: For code refactoring
        
        Requirements: 3.1.1, 3.1.2, 3.1.3
        """
        # Feature template (Requirement 3.1.1)
        feature = TaskTemplate(
            name="feature",
            title="实现 {feature_name} 功能",
            description="""### 功能描述
{description}

### 实现要点
- 设计数据模型
- 实现核心逻辑
- 编写单元测试
- 更新文档

### 验收标准
- [ ] 功能正常工作
- [ ] 测试覆盖率 >= 80%
- [ ] 代码审查通过""",
            priority=Priority.REQUIRED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("feature_name", "请输入功能名称", required=True),
                TemplatePrompt("description", "请输入功能描述", required=True, multiline=True)
            ]
        )
        
        # Bugfix template (Requirement 3.1.2)
        bugfix = TaskTemplate(
            name="bugfix",
            title="修复 {bug_description}",
            description="""### Bug 描述
{description}

### 复现步骤
{reproduction_steps}

### 修复方案
{fix_plan}""",
            priority=Priority.REQUIRED,
            estimated_effort=2,
            prompts=[
                TemplatePrompt("bug_description", "请输入Bug简短描述", required=True),
                TemplatePrompt("description", "请输入详细Bug描述", required=True, multiline=True),
                TemplatePrompt("reproduction_steps", "请输入复现步骤", required=True, multiline=True),
                TemplatePrompt("fix_plan", "请输入修复方案", required=False, multiline=True, default="待分析")
            ]
        )
        
        # Refactor template (Requirement 3.1.3)
        refactor = TaskTemplate(
            name="refactor",
            title="重构 {module_name}",
            description="""### 重构目标
{goal}

### 重构范围
{scope}

### 验收标准
- [ ] 功能行为不变
- [ ] 测试全部通过
- [ ] 代码质量提升""",
            priority=Priority.RECOMMENDED,
            estimated_effort=3,
            prompts=[
                TemplatePrompt("module_name", "请输入模块名称", required=True),
                TemplatePrompt("goal", "请输入重构目标", required=True, multiline=True),
                TemplatePrompt("scope", "请输入重构范围", required=True, multiline=True)
            ]
        )
        
        self._built_in_templates = {
            "feature": feature,
            "bugfix": bugfix,
            "refactor": refactor
        }
        
        logger.debug(f"Loaded {len(self._built_in_templates)} built-in templates")
    
    def load_custom_templates(self) -> Dict[str, TaskTemplate]:
        """Load custom templates from .harness/templates/
        
        Scans the custom_template_dir for .json files and attempts to load
        each as a TaskTemplate. Invalid templates are skipped with a warning.
        
        Returns:
            Dictionary mapping template names to TaskTemplate objects
            
        Requirements: 3.4
        """
        if not self.custom_template_dir.exists():
            logger.debug("Custom template directory doesn't exist, using built-in only")
            return {}
        
        custom = {}
        for json_file in self.custom_template_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                template = TaskTemplate.from_dict(data)
                
                # Validate
                errors = template.validate()
                if errors:
                    logger.warning(f"Template {json_file.name} has errors: {errors}")
                    continue
                
                custom[template.name] = template
                logger.debug(f"Loaded custom template '{template.name}' from {json_file.name}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON in {json_file}: {e}")
            except Exception as e:
                logger.error(f"Failed to load template {json_file}: {e}")
        
        return custom
    
    def get_all_templates(self) -> Dict[str, TaskTemplate]:
        """Get all templates (custom templates override built-in)
        
        Merges built-in and custom templates. If a custom template has the
        same name as a built-in template, the custom template takes precedence.
        
        Returns:
            Dictionary mapping template names to TaskTemplate objects
            
        Requirements: 3.1, 3.4
        """
        templates = dict(self._built_in_templates)
        custom = self.load_custom_templates()
        templates.update(custom)  # Custom templates can override built-in
        return templates
    
    def get_template(self, name: str) -> Optional[TaskTemplate]:
        """Get specific template by name
        
        Args:
            name: Name of the template to retrieve
            
        Returns:
            TaskTemplate object if found, None otherwise
            
        Requirements: 3.1, 3.4
        """
        templates = self.get_all_templates()
        return templates.get(name)
    
    def list_templates(self) -> List[Tuple[str, TaskTemplate, bool]]:
        """List all templates with (name, template, is_custom) tuples
        
        Returns a list of tuples, where each tuple contains:
        - name: Template name
        - template: TaskTemplate object
        - is_custom: True if custom template, False if built-in
        
        If a custom template overrides a built-in template, only the custom
        template is included in the result (marked as custom).
        
        Returns:
            List of (name, template, is_custom) tuples
            
        Requirements: 3.1, 3.4
        """
        built_in = {name: (name, template, False) 
                    for name, template in self._built_in_templates.items()}
        custom = {name: (name, template, True) 
                  for name, template in self.load_custom_templates().items()}
        
        # Merge, with custom overriding built-in
        result = dict(built_in)
        result.update(custom)
        return list(result.values())
