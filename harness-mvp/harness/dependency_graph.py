"""任务依赖可视化 - 生成 Mermaid 依赖图"""
from collections import defaultdict, deque
from typing import List, Dict, Set, Tuple, Optional
from harness.models import Task, TaskStatus, Priority


def generate_mermaid_graph(tasks: List[Task]) -> str:
    """生成 Mermaid 格式的任务依赖图

    Args:
        tasks: 任务列表

    Returns:
        Mermaid 格式的图定义字符串
    """
    if not tasks:
        return "graph TD\n    empty[\"暂无任务\"]"

    task_map = {t.id: t for t in tasks}
    lines = ["graph TD"]
    lines.append("")

    # 检测循环依赖
    cycles = detect_cycles(tasks)

    # 建立依赖关系
    has_deps = any(t.dependencies for t in tasks)

    for task in sorted(tasks, key=lambda t: t.id):
        node_id = f"T{task.id}"
        label = _escape_mermaid(f"{task.id}: {task.title}")
        status_class = _status_to_class(task.status)
        node_style = f"style {node_id} {status_class}"

        if task.id in cycles:
            # 循环依赖节点用红色高亮
            lines.append(f"    {node_id}[\"{label}\"]")
            lines.append(f"    style {node_id} fill:#ff4444,stroke:#cc0000,color:#fff")
            lines.append(f"    class {node_id} cycleNode")
        else:
            lines.append(f"    {node_id}[\"{label}\"]")
            lines.append(f"    style {node_id} {status_class}")

    lines.append("")

    # 如果没有任何依赖关系，显示独立节点布局
    if not has_deps:
        # 按优先级分组排列
        req_nodes = [f"T{t.id}" for t in tasks if t.priority == Priority.REQUIRED]
        rec_nodes = [f"T{t.id}" for t in tasks if t.priority == Priority.RECOMMENDED]
        opt_nodes = [f"T{t.id}" for t in tasks if t.priority == Priority.OPTIONAL]

        if len(tasks) > 1:
            # 用子图表示优先级分组
            if req_nodes:
                lines.append("    subgraph Required[必需任务]")
                for n in req_nodes:
                    lines.append(f"        {n}")
                lines.append("    end")
                lines.append("")
            if rec_nodes:
                lines.append("    subgraph Recommended[推荐任务]")
                for n in rec_nodes:
                    lines.append(f"        {n}")
                lines.append("    end")
                lines.append("")
            if opt_nodes:
                lines.append("    subgraph Optional[可选任务]")
                for n in opt_nodes:
                    lines.append(f"        {n}")
                lines.append("    end")
                lines.append("")

        return "\n".join(lines)

    # 有依赖关系：按依赖绘图
    edges: List[Tuple[int, int]] = []
    for task in tasks:
        for dep_id in task.dependencies:
            if dep_id in task_map:
                edges.append((task.id, dep_id))

    # 拓扑排序分组（用于布局）
    try:
        batches = _topological_sort(tasks, task_map)
        # 同批次（同层）节点用虚线连接辅助布局
        for batch in batches:
            for i in range(len(batch) - 1):
                if _is_same_priority_and_status(batch[i], batch[i + 1]):
                    pass  # 不添加辅助边，保持简洁
    except ValueError:
        pass  # 循环依赖，跳过批次布局

    # 绘制依赖边（方向从依赖指向任务）
    drawn = set()
    for task_id, dep_id in edges:
        if (task_id, dep_id) not in drawn:
            drawn.add((task_id, dep_id))
            lines.append(f"    T{dep_id} --> T{task_id}")

    # 添加图例
    lines.append("")
    lines.append("    subgraph Legend[图例]")
    lines.append("        L_done[\"✅ DONE\"]")
    lines.append("        L_wip[\"🔧 WIP\"]")
    lines.append("        L_todo[\"⬜ TODO\"]")
    lines.append("        L_blocked[\"🔴 BLOCKED\"]")
    lines.append("    end")
    lines.append(f"    style L_done {_status_to_class(TaskStatus.DONE)}")
    lines.append(f"    style L_wip {_status_to_class(TaskStatus.WIP)}")
    lines.append(f"    style L_todo {_status_to_class(TaskStatus.TODO)}")
    lines.append(f"    style L_blocked {_status_to_class(TaskStatus.BLOCKED)}")

    return "\n".join(lines)


def detect_cycles(tasks: List[Task]) -> Set[int]:
    """检测循环依赖中的节点

    使用 DFS 检测有向图中的环。

    Args:
        tasks: 任务列表

    Returns:
        参与循环依赖的任务 ID 集合
    """
    task_map = {t.id: t for t in tasks}
    adj: Dict[int, List[int]] = defaultdict(list)

    for task in tasks:
        for dep_id in task.dependencies:
            if dep_id in task_map:
                adj[dep_id].append(task.id)

    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[int, int] = defaultdict(int)
    in_cycle: Set[int] = set()

    def dfs(node: int, path: Set[int]):
        color[node] = GRAY
        path.add(node)
        for neighbor in adj[node]:
            if neighbor in color and color[neighbor] == BLACK:
                continue
            if neighbor in path:
                # 发现环，标记环上所有节点
                in_cycle.add(node)
                # 回溯标记环上的所有节点
                n = neighbor
                for p in list(path):
                    in_cycle.add(p)
                continue
            if color[neighbor] == WHITE:
                dfs(neighbor, path)
        path.discard(node)
        color[node] = BLACK

    for task in tasks:
        if color[task.id] == WHITE:
            dfs(task.id, set())

    return in_cycle


def find_critical_path(tasks: List[Task]) -> List[Task]:
    """找到关键路径（最长 Required 依赖链）

    关键路径是必须（REQUIRED）任务中最长的依赖链，
    决定了项目的最短完成时间。

    Args:
        tasks: 任务列表

    Returns:
        关键路径上的任务列表（从依赖到被依赖）
    """
    task_map = {t.id: t for t in tasks}
    dep_graph: Dict[int, List[int]] = defaultdict(list)
    in_degree: Dict[int, int] = defaultdict(int)

    for task in tasks:
        if task.priority != Priority.REQUIRED:
            continue
        for dep_id in task.dependencies:
            if dep_id in task_map and task_map[dep_id].priority == Priority.REQUIRED:
                dep_graph[dep_id].append(task.id)
                in_degree[task.id] += 1
                if dep_id not in in_degree:
                    in_degree[dep_id] = 0

    if not dep_graph:
        return []

    # 最长路径（权重 = 估算工作量）
    dist: Dict[int, int] = {}
    prev: Dict[int, Optional[int]] = {}
    for t in tasks:
        if t.priority == Priority.REQUIRED:
            dist[t.id] = 0
            prev[t.id] = None

    # 拓扑序 DP
    try:
        ordered = _topological_sort(
            [t for t in tasks if t.priority == Priority.REQUIRED],
            task_map
        )
        flat = [t.id for batch in ordered for t in batch]

        for tid in flat:
            if tid not in dist:
                continue
            task = task_map[tid]
            for neighbor in dep_graph[tid]:
                new_dist = dist[tid] + (task_map[neighbor].estimated_effort if neighbor in task_map else 1)
                if new_dist > dist.get(neighbor, 0):
                    dist[neighbor] = new_dist
                    prev[neighbor] = tid
    except ValueError:
        return []

    if not dist:
        return []

    # 找最长路径终点
    end = max(dist, key=lambda k: dist[k])  # type: ignore
    if dist[end] == 0:
        return []

    # 回溯路径
    path: List[Task] = []
    cur = end
    while cur is not None:
        if cur in task_map:
            path.append(task_map[cur])
        cur = prev.get(cur)
    path.reverse()
    return path


def generate_graph_report(tasks: List[Task]) -> str:
    """生成依赖图分析报告

    Args:
        tasks: 任务列表

    Returns:
        格式化的报告文本
    """
    if not tasks:
        return "暂无任务"

    lines: List[str] = []
    lines.append("=" * 50)
    lines.append("任务依赖分析报告")
    lines.append("=" * 50)
    lines.append(f"总任务数: {len(tasks)}")

    # 任务状态统计
    status_counts = defaultdict(int)
    for t in tasks:
        status_counts[t.status.value] += 1
    lines.append("")
    lines.append("状态分布:")
    for status, count in sorted(status_counts.items()):
        lines.append(f"  {status}: {count}")

    # 依赖分析
    task_map = {t.id: t for t in tasks}
    with_deps = sum(1 for t in tasks if t.dependencies)
    lines.append("")
    lines.append(f"有依赖的任务: {with_deps}/{len(tasks)}")
    lines.append(f"无依赖的任务: {len(tasks) - with_deps}/{len(tasks)}")

    # 循环依赖
    cycles = detect_cycles(tasks)
    if cycles:
        lines.append("")
        lines.append("⚠️ 检测到循环依赖!")
        for tid in sorted(cycles):
            task = task_map.get(tid)
            if task:
                lines.append(f"  - Task {tid}: {task.title}")
    else:
        lines.append("")
        lines.append("✅ 无循环依赖")

    # 关键路径
    critical = find_critical_path(tasks)
    if critical:
        lines.append("")
        lines.append("关键路径 (最长 Required 链):")
        total_effort = sum(t.estimated_effort for t in critical)
        for t in critical:
            done_mark = "✅" if t.status == TaskStatus.DONE else "⬜"
            lines.append(f"  {done_mark} Task {t.id}: {t.title} (工作量: {t.estimated_effort})")
        lines.append(f"  总工作量: {total_effort}")

    # 按批次分析
    try:
        batches = _topological_sort(tasks, task_map)
        lines.append("")
        lines.append("执行批次 (拓扑排序):")
        for i, batch in enumerate(batches, 1):
            task_names = [f"Task {t.id}" for t in batch]
            lines.append(f"  批次 {i}: {', '.join(task_names)}")
    except ValueError:
        lines.append("")
        lines.append("⚠️ 存在循环依赖，无法计算执行批次")

    lines.append("")
    lines.append("=" * 50)
    return "\n".join(lines)


# ===== 内部工具函数 =====


def _topological_sort(tasks: List[Task], task_map: Dict[int, Task]) -> List[List[Task]]:
    """拓扑排序，返回按依赖顺序排列的批次列表

    Args:
        tasks: 任务列表
        task_map: 任务 ID 到 Task 的映射

    Returns:
        批次列表，每个批次是一组可并行执行的任务

    Raises:
        ValueError: 存在循环依赖
    """
    adj: Dict[int, List[int]] = defaultdict(list)
    in_degree: Dict[int, int] = defaultdict(int)

    for task in tasks:
        if task.id not in in_degree:
            in_degree[task.id] = 0
        for dep_id in task.dependencies:
            if dep_id in task_map:
                adj[dep_id].append(task.id)
                in_degree[task.id] += 1

    queue = deque([t.id for t in tasks if in_degree.get(t.id, 0) == 0])
    visited = 0
    batches = []

    batch_map: Dict[int, int] = {}

    while queue:
        batch = list(queue)
        queue.clear()
        current_batch = []
        for node_id in batch:
            current_batch.append(task_map[node_id])
            visited += 1
            for neighbor in adj[node_id]:
                if neighbor not in task_map:
                    continue
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if current_batch:
            batches.append(current_batch)

    if visited != len(tasks):
        raise ValueError("检测到循环依赖")

    return batches


def _status_to_class(status: TaskStatus) -> str:
    """任务状态转 Mermaid 样式

    Args:
        status: 任务状态

    Returns:
        Mermaid style 字符串
    """
    styles = {
        TaskStatus.DONE: "fill:#4caf50,stroke:#2e7d32,color:#fff",
        TaskStatus.WIP: "fill:#2196f3,stroke:#1565c0,color:#fff",
        TaskStatus.TODO: "fill:#e0e0e0,stroke:#9e9e9e,color:#000",
        TaskStatus.BLOCKED: "fill:#f44336,stroke:#b71c1c,color:#fff",
    }
    return styles.get(status, "fill:#e0e0e0,stroke:#9e9e9e,color:#000")


def _escape_mermaid(text: str) -> str:
    """转义 Mermaid 文本中的特殊字符

    Args:
        text: 原始文本

    Returns:
        转义后的文本
    """
    return text.replace('"', "'").replace("(", "（").replace(")", "）")


def _is_same_priority_and_status(t1: Task, t2: Task) -> bool:
    """判断两个任务是否有相同优先级和状态"""
    return t1.priority == t2.priority and t1.status == t2.status
