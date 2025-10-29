#!/bin/bash

# 费用跟踪系统 Docker 停止脚本

echo "🛑 停止费用跟踪系统..."

# 停止所有服务
docker-compose down

echo "✅ 服务已停止"
echo ""
echo "💡 如需完全清理（包括数据卷），请运行: docker-compose down -v"
echo "💡 如需删除镜像，请运行: docker-compose down --rmi all"
