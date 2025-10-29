#!/bin/bash

# Docker 快速测试脚本

echo "🧪 Docker 快速测试脚本"
echo "========================"

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

echo "✅ Docker 正在运行"

# 检查必要文件是否存在
echo "📁 检查必要文件..."

files=("Dockerfile.backend" "Dockerfile.frontend" "docker-compose.yml" "nginx.conf")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
        exit 1
    fi
done

echo ""
echo "🔨 开始构建镜像..."

# 构建镜像
if docker-compose build; then
    echo "✅ 镜像构建成功"
else
    echo "❌ 镜像构建失败"
    exit 1
fi

echo ""
echo "🚀 启动服务..."

# 启动服务
if docker-compose up -d; then
    echo "✅ 服务启动成功"
else
    echo "❌ 服务启动失败"
    exit 1
fi

echo ""
echo "⏳ 等待服务就绪..."
sleep 15

echo ""
echo "🔍 检查服务状态..."
docker-compose ps

echo ""
echo "🌐 测试服务连接..."

# 测试后端健康检查
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务正常 (http://localhost:8000/health)"
else
    echo "❌ 后端服务异常"
fi

# 测试前端服务
if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ 前端服务正常 (http://localhost)"
else
    echo "❌ 前端服务异常"
fi

echo ""
echo "📊 服务访问地址："
echo "🌐 前端: http://localhost"
echo "🔧 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "📝 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
