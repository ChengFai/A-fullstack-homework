# Makefile for Python project with Black formatting

.PHONY: help install format format-check sort-imports lint test clean

help:  ## 显示帮助信息
	@echo "可用的命令："
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 安装开发依赖
	uv sync --extra dev

format:  ## 使用 Black 格式化所有 Python 文件
	uv run black .

format-check:  ## 检查代码格式（不修改文件）
	uv run black --check .

sort-imports:  ## 使用 isort 排序导入语句
	uv run isort .

sort-imports-check:  ## 检查导入排序（不修改文件）
	uv run isort --check-only .

lint: format-check sort-imports-check  ## 运行所有代码质量检查

test:  ## 运行测试
	python run_tests.py

clean:  ## 清理缓存文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
