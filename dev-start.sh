#!/bin/bash

# 费用跟踪系统开发环境一键启动脚本
# 支持本地开发模式和Docker模式启动

set -e  # 遇到错误立即退出

# 默认启动模式
MODE="local"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            MODE="docker"
            shift
            ;;
        --local)
            MODE="local"
            shift
            ;;
        -h|--help)
            echo "费用跟踪系统开发环境启动脚本"
            echo ""
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --docker    使用Docker模式启动（推荐用于生产环境测试）"
            echo "  --local     使用本地开发模式启动（默认，推荐用于开发）"
            echo "  -h, --help  显示此帮助信息"
            echo ""
            echo "示例:"
            echo "  $0           # 本地开发模式"
            echo "  $0 --local   # 本地开发模式"
            echo "  $0 --docker  # Docker模式"
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 -h 或 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

if [ "$MODE" = "docker" ]; then
    echo "🐳 启动费用跟踪系统Docker环境..."
else
    echo "🚀 启动费用跟踪系统开发环境..."
fi

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Docker环境
check_docker_requirements() {
    echo -e "${BLUE}📋 检查Docker环境要求...${NC}"
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose 未安装，请先安装 Docker Compose${NC}"
        exit 1
    fi
    
    # 检查 Docker 是否运行
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker 未运行，请先启动 Docker${NC}"
        exit 1
    fi
    
    # 检查必要文件是否存在
    echo "检查Docker配置文件..."
    files=("Dockerfile.backend" "Dockerfile.frontend" "docker-compose.yml" "nginx.conf")
    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            echo -e "${RED}❌ $file 不存在${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✅ Docker环境检查完成${NC}"
}

# 检查本地开发环境要求
check_local_requirements() {
    echo -e "${BLUE}📋 检查本地开发环境要求...${NC}"
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js 未安装，请先安装 Node.js${NC}"
        exit 1
    fi
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm 未安装，请先安装 npm${NC}"
        exit 1
    fi
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 未安装，请先安装 Python3${NC}"
        exit 1
    fi
    
    # 检查 uv (Python 包管理器)
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}⚠️  uv 未安装，尝试使用 pip 安装...${NC}"
        pip3 install uv
    fi
    
    echo -e "${GREEN}✅ 本地开发环境检查完成${NC}"
}

# 安装前端依赖
install_frontend_deps() {
    echo -e "${BLUE}📦 安装前端依赖...${NC}"
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "安装 npm 依赖..."
        npm install
    else
        echo "前端依赖已存在，跳过安装"
    fi
    
    cd ..
    echo -e "${GREEN}✅ 前端依赖安装完成${NC}"
}

# 安装后端依赖
install_backend_deps() {
    echo -e "${BLUE}📦 安装后端依赖...${NC}"
    cd backend
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d ".venv" ]; then
        echo "创建 Python 虚拟环境..."
        uv venv
    fi
    
    # 激活虚拟环境并安装依赖
    echo "安装 Python 依赖..."
    uv pip install -e .
    
    cd ..
    echo -e "${GREEN}✅ 后端依赖安装完成${NC}"
}

# 启动后端服务
start_backend() {
    echo -e "${BLUE}🔧 启动后端服务...${NC}"
    cd backend
    
    # 在后台启动后端服务
    uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
}

# 启动前端服务
start_frontend() {
    echo -e "${BLUE}🎨 启动前端服务...${NC}"
    cd frontend
    
    # 在后台启动前端服务
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    echo -e "${GREEN}✅ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
}

# Docker模式启动函数
start_docker_services() {
    echo -e "${BLUE}🐳 启动Docker服务...${NC}"
    
    # 检查是否存在 .env 文件
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  未找到 .env 文件，使用默认配置${NC}"
        echo -e "${YELLOW}💡 如需自定义配置，请复制 env.example 为 .env 并修改${NC}"
    fi
    
    # 停止可能存在的旧容器
    echo "清理旧容器..."
    docker-compose down 2>/dev/null || true
    
    # 构建镜像
    echo -e "${BLUE}📦 构建Docker镜像...${NC}"
    docker-compose build
    
    # 启动服务
    echo -e "${BLUE}🏃 启动Docker服务...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}✅ Docker服务已启动${NC}"
}

# Docker模式等待服务启动
wait_for_docker_services() {
    echo -e "${BLUE}⏳ 等待Docker服务启动...${NC}"
    
    # 等待数据库服务启动
    echo "等待数据库服务启动..."
    for i in {1..60}; do
        if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 数据库服务已就绪${NC}"
            break
        fi
        sleep 2
    done
    
    # 等待后端服务启动
    echo "等待后端服务启动..."
    for i in {1..60}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 后端服务已就绪${NC}"
            break
        fi
        sleep 2
    done
    
    # 等待前端服务启动
    echo "等待前端服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 前端服务已就绪${NC}"
            break
        fi
        sleep 2
    done
}

# Docker模式显示服务信息
show_docker_service_info() {
    echo ""
    echo -e "${GREEN}🎉 Docker服务启动完成！${NC}"
    echo ""
    echo -e "${BLUE}📊 服务信息：${NC}"
    echo -e "  🌐 前端地址: ${YELLOW}http://localhost${NC}"
    echo -e "  🔧 后端API: ${YELLOW}http://localhost:8000${NC}"
    echo -e "  📚 API文档: ${YELLOW}http://localhost:8000/docs${NC}"
    echo -e "  ❤️  健康检查: ${YELLOW}http://localhost:8000/health${NC}"
    echo -e "  🗄️  数据库: ${YELLOW}localhost:5432${NC}"
    echo ""
    echo -e "${BLUE}📝 Docker管理命令：${NC}"
    echo -e "  🛑 停止服务: ${YELLOW}docker-compose down${NC}"
    echo -e "  📋 查看日志: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "  🔍 查看状态: ${YELLOW}docker-compose ps${NC}"
    echo -e "  🔄 重启服务: ${YELLOW}docker-compose restart${NC}"
    echo ""
    echo -e "${YELLOW}💡 提示: 按 Ctrl+C 停止所有服务${NC}"
}

# Docker模式清理函数
cleanup_docker() {
    echo ""
    echo -e "${YELLOW}🛑 正在停止Docker服务...${NC}"
    
    # 停止Docker服务
    docker-compose down
    
    echo -e "${GREEN}🎯 Docker服务已停止${NC}"
    exit 0
}

# 等待服务启动
wait_for_services() {
    echo -e "${BLUE}⏳ 等待服务启动...${NC}"
    
    # 等待后端服务启动
    echo "等待后端服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 后端服务已就绪${NC}"
            break
        fi
        sleep 1
    done
    
    # 等待前端服务启动
    echo "等待前端服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 前端服务已就绪${NC}"
            break
        fi
        sleep 1
    done
}

# 显示服务信息
show_service_info() {
    echo ""
    echo -e "${GREEN}🎉 服务启动完成！${NC}"
    echo ""
    echo -e "${BLUE}📊 服务信息：${NC}"
    echo -e "  🌐 前端地址: ${YELLOW}http://localhost:5173${NC}"
    echo -e "  🔧 后端API: ${YELLOW}http://localhost:8000${NC}"
    echo -e "  📚 API文档: ${YELLOW}http://localhost:8000/docs${NC}"
    echo -e "  ❤️  健康检查: ${YELLOW}http://localhost:8000/health${NC}"
    echo ""
    echo -e "${BLUE}📝 管理命令：${NC}"
    echo -e "  🛑 停止服务: ${YELLOW}./dev-stop.sh${NC}"
    echo -e "  📋 查看日志: ${YELLOW}tail -f backend/logs/*.log${NC}"
    echo ""
    echo -e "${YELLOW}💡 提示: 按 Ctrl+C 停止所有服务${NC}"
}

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 正在停止服务...${NC}"
    
    # 停止后端服务
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ 后端服务已停止${NC}"
    fi
    
    # 停止前端服务
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ 前端服务已停止${NC}"
    fi
    
    # 清理可能残留的进程
    pkill -f "uvicorn src.app.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    echo -e "${GREEN}🎯 所有服务已停止${NC}"
    exit 0
}

# 本地开发模式主流程
main_local() {
    check_local_requirements
    install_frontend_deps
    install_backend_deps
    start_backend
    start_frontend
    wait_for_services
    show_service_info
    
    # 保持脚本运行，等待用户中断
    echo -e "${BLUE}🔄 服务运行中，按 Ctrl+C 停止...${NC}"
    wait
}

# Docker模式主流程
main_docker() {
    check_docker_requirements
    start_docker_services
    wait_for_docker_services
    show_docker_service_info
    
    # 保持脚本运行，等待用户中断
    echo -e "${BLUE}🔄 Docker服务运行中，按 Ctrl+C 停止...${NC}"
    wait
}

# 主执行流程
main() {
    if [ "$MODE" = "docker" ]; then
        # 设置Docker模式的信号处理
        trap cleanup_docker SIGINT SIGTERM
        main_docker
    else
        # 设置本地模式的信号处理
        trap cleanup SIGINT SIGTERM
        main_local
    fi
}

# 执行主函数
main "$@"
