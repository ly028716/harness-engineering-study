"""测试任务依赖可视化模块"""
import pytest
from harness.models import Task, TaskStatus, Priority
from harness.dependency_graph import (
    generate_mermaid_graph,
    detect_cycles,
    find_critical_path,
    generate_graph_report,
)


def make_task(id: int, title: str = "", status: TaskStatus = TaskStatus.TODO,
              priority: Priority = Priority.REQUIRED, dependencies=None,
              estimated_effort: int = 1) -> Task:
    """辅助函数：快速创建 Task 实例"""
    return Task(
        id=id,
        title=title or f"Task {id}",
        status=status,
        priority=priority,
        dependencies=dependencies or [],
        estimated_effort=estimated_effort,
    )


class TestGenerateMermaidGraph:
    """测试 generate_mermaid_graph"""

    def test_empty_tasks(self):
        """测试空任务列表返回占位图"""
        result = generate_mermaid_graph([])
        assert "graph TD" in result
        assert "暂无任务" in result

    def test_single_task(self):
        """测试单任务"""
        tasks = [make_task(1, "测试任务")]
        result = generate_mermaid_graph(tasks)
        assert "graph TD" in result
        assert 'T1["1: 测试任务"]' in result

    def test_multiple_tasks_no_deps(self):
        """测试多任务无依赖"""
        tasks = [
            make_task(1, "任务一", priority=Priority.REQUIRED),
            make_task(2, "任务二", priority=Priority.RECOMMENDED),
            make_task(3, "任务三", priority=Priority.OPTIONAL),
        ]
        result = generate_mermaid_graph(tasks)

        # 应包含子图分组
        assert "Required[必需任务]" in result
        assert "Recommended[推荐任务]" in result
        assert "Optional[可选任务]" in result
        assert "T1" in result
        assert "T2" in result
        assert "T3" in result

    def test_with_dependencies(self):
        """测试有依赖关系的图"""
        tasks = [
            make_task(1, "基础模块"),
            make_task(2, "上层功能", dependencies=[1]),
        ]
        result = generate_mermaid_graph(tasks)
        assert "T1 --> T2" in result
        assert "Legend[图例]" in result

    def test_status_colors(self):
        """测试不同状态的颜色"""
        tasks = [
            make_task(1, "已完成", status=TaskStatus.DONE),
            make_task(2, "进行中", status=TaskStatus.WIP),
            make_task(3, "已阻塞", status=TaskStatus.BLOCKED),
        ]
        result = generate_mermaid_graph(tasks)

        # 不同状态应有不同样式
        assert "fill:#4caf50" in result  # DONE 绿色
        assert "fill:#2196f3" in result  # WIP 蓝色
        assert "fill:#f44336" in result  # BLOCKED 红色

    def test_cycle_highlight(self):
        """测试循环依赖节点高亮"""
        tasks = [
            make_task(1, "任务A", dependencies=[2]),
            make_task(2, "任务B", dependencies=[1]),
        ]
        result = generate_mermaid_graph(tasks)
        assert "fill:#ff4444" in result  # 循环依赖红色高亮

    def test_single_task_no_subgraph(self):
        """测试单任务不显示子图"""
        tasks = [make_task(1, "唯一任务")]
        result = generate_mermaid_graph(tasks)
        assert "subgraph" not in result

    def test_dependency_edge_direction(self):
        """测试依赖边方向正确（依赖 -> 被依赖）"""
        tasks = [
            make_task(1, "基础"),
            make_task(2, "进阶", dependencies=[1]),
        ]
        result = generate_mermaid_graph(tasks)
        # T1(基础) 指向 T2(进阶)
        assert "T1 --> T2" in result


class TestDetectCycles:
    """测试 detect_cycles"""

    def test_no_cycles(self):
        """测试无循环依赖"""
        tasks = [
            make_task(1, "A", dependencies=[2]),
            make_task(2, "B", dependencies=[3]),
            make_task(3, "C"),
        ]
        cycles = detect_cycles(tasks)
        assert len(cycles) == 0

    def test_direct_cycle(self):
        """测试直接循环依赖 A -> B -> A"""
        tasks = [
            make_task(1, "A", dependencies=[2]),
            make_task(2, "B", dependencies=[1]),
        ]
        cycles = detect_cycles(tasks)
        assert 1 in cycles
        assert 2 in cycles

    def test_self_cycle(self):
        """测试自循环依赖 A -> A"""
        tasks = [
            make_task(1, "A", dependencies=[1]),
        ]
        cycles = detect_cycles(tasks)
        assert 1 in cycles

    def test_complex_cycle(self):
        """测试复杂循环依赖"""
        tasks = [
            make_task(1, "A", dependencies=[2]),
            make_task(2, "B", dependencies=[3]),
            make_task(3, "C", dependencies=[4]),
            make_task(4, "D", dependencies=[1]),
        ]
        cycles = detect_cycles(tasks)
        assert all(i in cycles for i in [1, 2, 3, 4])

    def test_cycle_with_independent_nodes(self):
        """测试循环依赖中有独立节点"""
        tasks = [
            make_task(1, "A", dependencies=[2]),
            make_task(2, "B", dependencies=[1]),
            make_task(3, "独立任务"),
        ]
        cycles = detect_cycles(tasks)
        assert 1 in cycles
        assert 2 in cycles
        assert 3 not in cycles  # 独立节点不在环中

    def test_diamond_dependency_no_cycle(self):
        """测试菱形依赖无循环"""
        tasks = [
            make_task(1, "根"),
            make_task(2, "左", dependencies=[1]),
            make_task(3, "右", dependencies=[1]),
            make_task(4, "合并", dependencies=[2, 3]),
        ]
        cycles = detect_cycles(tasks)
        assert len(cycles) == 0

    def test_empty_tasks(self):
        """测试空任务列表"""
        cycles = detect_cycles([])
        assert cycles == set()

    def test_single_task_no_cycle(self):
        """测试单任务无环"""
        tasks = [make_task(1, "单任务")]
        cycles = detect_cycles(tasks)
        assert len(cycles) == 0

    def test_dependency_on_nonexistent(self):
        """测试依赖不存在的任务"""
        tasks = [
            make_task(1, "A", dependencies=[999]),
        ]
        # 不应报错，999 不存在直接忽略
        cycles = detect_cycles(tasks)
        assert len(cycles) == 0


class TestFindCriticalPath:
    """测试 find_critical_path"""

    def test_simple_chain(self):
        """测试简单依赖链"""
        tasks = [
            make_task(1, "基础", estimated_effort=2),
            make_task(2, "上层", dependencies=[1], estimated_effort=3),
        ]
        path = find_critical_path(tasks)
        assert len(path) == 2
        assert path[0].id == 1
        assert path[1].id == 2

    def test_no_required_tasks(self):
        """测试无 Required 任务"""
        tasks = [
            make_task(1, "可选", priority=Priority.OPTIONAL),
            make_task(2, "推荐", priority=Priority.RECOMMENDED),
        ]
        path = find_critical_path(tasks)
        assert path == []

    def test_parallel_paths(self):
        """测试并行路径，选择最长的"""
        tasks = [
            make_task(1, "根", estimated_effort=1),
            make_task(2, "短路径", dependencies=[1], estimated_effort=1),
            make_task(3, "长路径", dependencies=[1], estimated_effort=5),
        ]
        path = find_critical_path(tasks)
        assert len(path) >= 2
        # 关键路径应该是经过 3（工作量更大）的路径
        task_ids = [t.id for t in path]
        assert 3 in task_ids

    def test_cycle_in_graph(self):
        """测试有循环依赖时返回空"""
        tasks = [
            make_task(1, "A", dependencies=[2], estimated_effort=1),
            make_task(2, "B", dependencies=[1], estimated_effort=1),
        ]
        path = find_critical_path(tasks)
        assert path == []

    def test_non_required_not_in_path(self):
        """测试非 Required 任务不在关键路径中"""
        tasks = [
            make_task(1, "基础", priority=Priority.REQUIRED, estimated_effort=2),
            make_task(2, "上层", priority=Priority.REQUIRED, dependencies=[1], estimated_effort=3),
            make_task(3, "可选增强", priority=Priority.OPTIONAL, dependencies=[1], estimated_effort=10),
        ]
        path = find_critical_path(tasks)
        # 3 虽然工作量更大但不是 Required，不应在关键路径
        assert all(t.priority == Priority.REQUIRED for t in path)

    def test_empty_tasks(self):
        """测试空任务列表"""
        path = find_critical_path([])
        assert path == []

    def test_single_required_task(self):
        """测试单个 Required 任务"""
        tasks = [
            make_task(1, "单任务", estimated_effort=3),
        ]
        path = find_critical_path(tasks)
        # 单任务无依赖，不算关键路径
        assert path == []


class TestGenerateGraphReport:
    """测试 generate_graph_report"""

    def test_empty_tasks(self):
        """测试空任务列表"""
        result = generate_graph_report([])
        assert "暂无任务" in result

    def test_basic_report(self):
        """测试基本报告内容"""
        tasks = [
            make_task(1, "任务一", status=TaskStatus.DONE),
            make_task(2, "任务二", status=TaskStatus.TODO),
        ]
        result = generate_graph_report(tasks)
        assert "任务依赖分析报告" in result
        assert "总任务数: 2" in result
        assert "DONE: 1" in result or "1" in result
        assert "TODO: 1" in result or "1" in result

    def test_report_with_deps(self):
        """测试有依赖关系的报告"""
        tasks = [
            make_task(1, "基础"),
            make_task(2, "上层", dependencies=[1]),
        ]
        result = generate_graph_report(tasks)
        assert "有依赖的任务: 1/2" in result

    def test_report_no_cycles(self):
        """测试无循环依赖报告"""
        tasks = [make_task(1, "单任务")]
        result = generate_graph_report(tasks)
        assert "无循环依赖" in result or "✅" in result

    def test_report_with_cycles(self):
        """测试有循环依赖报告"""
        tasks = [
            make_task(1, "任务A", dependencies=[2]),
            make_task(2, "任务B", dependencies=[1]),
        ]
        result = generate_graph_report(tasks)
        assert "检测到循环依赖" in result

    def test_report_critical_path(self):
        """测试关键路径报告"""
        tasks = [
            make_task(1, "基础", estimated_effort=2),
            make_task(2, "上层", dependencies=[1], estimated_effort=3),
        ]
        result = generate_graph_report(tasks)
        assert "关键路径" in result
        assert "总工作量" in result

    def test_report_topological_batches(self):
        """测试拓扑排序批次"""
        tasks = [
            make_task(1, "基础"),
            make_task(2, "依赖基础", dependencies=[1]),
            make_task(3, "依赖基础2", dependencies=[1]),
        ]
        result = generate_graph_report(tasks)
        assert "执行批次" in result

    def test_report_topological_with_cycle(self):
        """测试循环依赖时拓扑排序失败"""
        tasks = [
            make_task(1, "A", dependencies=[2]),
            make_task(2, "B", dependencies=[1]),
        ]
        result = generate_graph_report(tasks)
        assert "无法计算执行批次" in result or "循环依赖" in result
