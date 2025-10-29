#!/bin/bash

# 费用跟踪系统 Docker 快速启动脚本

echo "🚀 启动费用跟踪系统..."

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查是否存在 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，使用默认配置"
    echo "💡 如需自定义配置，请复制 env.example 为 .env 并修改"
fi

# 构建镜像
echo "📦 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "🏃 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 服务状态："
docker-compose ps

echo ""
echo "✅ 服务启动完成！"
echo "🌐 前端访问地址: http://localhost"
echo "🔧 后端API地址: http://localhost:8000"
echo "📊 API文档地址: http://localhost:8000/docs"
echo ""
echo "📝 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
