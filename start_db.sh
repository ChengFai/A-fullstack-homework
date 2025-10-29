#!/bin/bash

# 数据库集成启动脚本

echo "🚀 启动PostgreSQL数据库集成..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker Desktop"
    echo "安装方法:"
    echo "1. 访问 https://www.docker.com/products/docker-desktop/"
    echo "2. 下载并安装Docker Desktop for Mac"
    echo "3. 启动Docker Desktop"
    echo ""
    echo "或者使用Homebrew安装:"
    echo "brew install --cask docker"
    exit 1
fi

# 检查docker-compose是否可用
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose未找到，尝试使用docker compose..."
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "📊 启动PostgreSQL容器..."
$COMPOSE_CMD up -d postgres

echo "⏳ 等待数据库启动..."
sleep 5

echo "🔍 检查容器状态..."
$COMPOSE_CMD ps

echo "📝 查看数据库日志..."
$COMPOSE_CMD logs postgres

echo ""
echo "✅ PostgreSQL容器已启动！"
echo ""
echo "数据库连接信息:"
echo "- 主机: localhost"
echo "- 端口: 5432"
echo "- 数据库: expense_tracker"
echo "- 用户名: postgres"
echo "- 密码: password123"
echo ""
echo "下一步:"
echo "1. 运行数据库测试: python test_db_integration.py"
echo "2. 启动FastAPI服务器: cd backend && uv run uvicorn src.app.main:app --reload"
echo "3. 访问API文档: http://localhost:8000/docs"
