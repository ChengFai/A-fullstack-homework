# Black 代码格式化工具配置说明

## 什么是 Black？

Black 是一个 Python 代码格式化工具，被称为"不妥协的代码格式化器"。它能够：

- 自动格式化 Python 代码，确保符合 PEP 8 标准
- 提供一致的代码风格
- 零配置开箱即用
- 快速且可靠

## 安装和设置

### 1. 安装开发依赖

```bash
cd backend
uv sync --extra dev
```

### 2. 安装 pre-commit（可选但推荐）

```bash
pip install pre-commit
pre-commit install
```

## 使用方法

### 手动格式化

```bash
# 格式化所有 Python 文件
uv run black .

# 检查代码格式（不修改文件）
uv run black --check .

# 排序导入语句
uv run isort .

# 检查导入排序（不修改）
uv run isort --check-only .

# 运行所有代码质量检查
uv run black --check . && uv run isort --check-only .
```

### 使用 Black 命令行

```bash
# 格式化特定文件
black src/app/main.py

# 格式化整个项目
black .

# 检查格式（不修改）
black --check .

# 显示差异
black --diff .
```

### 使用 pre-commit（自动）

如果安装了 pre-commit，每次 `git commit` 时会自动运行格式化检查。

## 配置说明

### Black 配置（pyproject.toml）

```toml
[tool.black]
line-length = 88          # 行长度限制
target-version = ['py310'] # 目标 Python 版本
include = '\.pyi?$'       # 包含的文件类型
```

### isort 配置（与 Black 兼容）

```toml
[tool.isort]
profile = "black"         # 使用 Black 兼容的配置
line_length = 88          # 与 Black 保持一致
```

## IDE 集成

### VS Code

安装 Black 扩展，在设置中添加：

```json
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "editor.formatOnSave": true
}
```

### PyCharm

1. 安装 Black 插件
2. 在设置中配置 External Tools
3. 启用 "Reformat code" 选项

## 最佳实践

1. **提交前格式化**：使用 pre-commit 确保代码在提交前被格式化
2. **IDE 集成**：配置编辑器在保存时自动格式化
3. **CI/CD 集成**：在持续集成中运行格式检查
4. **团队协作**：确保所有团队成员使用相同的 Black 配置

## 常见问题

### Q: Black 改变了我不想要的格式
A: Black 的设计理念是"不妥协"，它优先考虑一致性而不是个人偏好。建议接受 Black 的格式化结果。

### Q: 如何排除某些文件？
A: 在 `pyproject.toml` 的 `[tool.black]` 部分添加 `extend-exclude` 配置。

### Q: 如何自定义行长度？
A: 修改 `pyproject.toml` 中的 `line-length` 设置（默认 88）。

## 相关工具

- **isort**：导入语句排序工具，与 Black 兼容
- **flake8**：代码风格检查工具
- **mypy**：静态类型检查工具
- **pre-commit**：Git 钩子管理工具
