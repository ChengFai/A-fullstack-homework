#!/usr/bin/env python3
"""
测试运行脚本
提供便捷的测试运行命令
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python run_tests.py unit          # 运行单元测试")
        print("  python run_tests.py integration  # 运行集成测试")
        print("  python run_tests.py all           # 运行所有测试")
        print("  python run_tests.py coverage      # 运行测试并生成覆盖率报告")
        print("  python run_tests.py fast          # 快速测试（无覆盖率）")
        print("  python run_tests.py install       # 安装测试依赖")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "install":
        print("安装测试依赖...")
        success = run_command(["uv", "sync", "--dev"], "安装开发依赖")
        if success:
            print("✅ 依赖安装成功")
        else:
            print("❌ 依赖安装失败")
            sys.exit(1)

    elif command == "unit":
        print("运行单元测试...")
        success = run_command(
            ["uv", "run", "python", "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
            "单元测试",
        )
        if success:
            print("✅ 单元测试通过")
        else:
            print("❌ 单元测试失败")
            sys.exit(1)

    elif command == "integration":
        print("运行集成测试...")
        success = run_command(
            [
                "uv",
                "run",
                "python",
                "-m",
                "pytest",
                "tests/integration/",
                "-v",
                "--tb=short",
            ],
            "集成测试",
        )
        if success:
            print("✅ 集成测试通过")
        else:
            print("❌ 集成测试失败")
            sys.exit(1)

    elif command == "all":
        print("运行所有测试...")
        success = run_command(
            ["uv", "run", "python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            "所有测试",
        )
        if success:
            print("✅ 所有测试通过")
        else:
            print("❌ 测试失败")
            sys.exit(1)

    elif command == "coverage":
        print("运行测试并生成覆盖率报告...")
        success = run_command(
            [
                "uv",
                "run",
                "python",
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--cov=src",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-fail-under=80",
            ],
            "测试覆盖率",
        )
        if success:
            print("✅ 测试通过，覆盖率报告已生成")
            print("📊 HTML覆盖率报告: htmlcov/index.html")
        else:
            print("❌ 测试失败或覆盖率不足")
            sys.exit(1)

    elif command == "fast":
        print("快速测试（无覆盖率）...")
        success = run_command(
            [
                "uv",
                "run",
                "python",
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "-x",  # 遇到第一个失败就停止
            ],
            "快速测试",
        )
        if success:
            print("✅ 快速测试通过")
        else:
            print("❌ 快速测试失败")
            sys.exit(1)

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
