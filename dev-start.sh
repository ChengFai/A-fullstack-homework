#!/bin/bash

# 费用跟踪系统开发环境一键启动脚本
# 同时启动前端和后端服务

set -e  # 遇到错误立即退出

echo "🚀 启动费用跟踪系统开发环境..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查必要的工具
check_requirements() {
    echo -e "${BLUE}📋 检查环境要求...${NC}"
    
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
    
    echo -e "${GREEN}✅ 环境检查完成${NC}"
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

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 主执行流程
main() {
    check_requirements
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

# 执行主函数
main "$@"
