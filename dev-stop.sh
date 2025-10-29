#!/bin/bash

# 费用跟踪系统开发环境停止脚本
# 停止所有运行的前后端服务

echo "🛑 停止费用跟踪系统开发环境..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 停止后端服务
stop_backend() {
    echo -e "${BLUE}🔧 停止后端服务...${NC}"
    
    # 查找并停止 uvicorn 进程
    BACKEND_PIDS=$(pgrep -f "uvicorn src.app.main:app" || true)
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo "找到后端进程: $BACKEND_PIDS"
        kill $BACKEND_PIDS
        echo -e "${GREEN}✅ 后端服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  未找到运行中的后端服务${NC}"
    fi
}

# 停止前端服务
stop_frontend() {
    echo -e "${BLUE}🎨 停止前端服务...${NC}"
    
    # 查找并停止 vite 进程
    FRONTEND_PIDS=$(pgrep -f "vite" || true)
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo "找到前端进程: $FRONTEND_PIDS"
        kill $FRONTEND_PIDS
        echo -e "${GREEN}✅ 前端服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  未找到运行中的前端服务${NC}"
    fi
}

# 停止所有相关进程
stop_all_processes() {
    echo -e "${BLUE}🧹 清理所有相关进程...${NC}"
    
    # 停止所有可能的进程
    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    pkill -f "node.*dev" 2>/dev/null || true
    
    echo -e "${GREEN}✅ 所有进程已清理${NC}"
}

# 检查端口占用
check_ports() {
    echo -e "${BLUE}🔍 检查端口占用情况...${NC}"
    
    # 检查后端端口 8000
    if lsof -i :8000 > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口 8000 仍被占用${NC}"
        lsof -i :8000
    else
        echo -e "${GREEN}✅ 端口 8000 已释放${NC}"
    fi
    
    # 检查前端端口 5173
    if lsof -i :5173 > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口 5173 仍被占用${NC}"
        lsof -i :5173
    else
        echo -e "${GREEN}✅ 端口 5173 已释放${NC}"
    fi
}

# 主执行流程
main() {
    stop_backend
    stop_frontend
    stop_all_processes
    
    # 等待进程完全停止
    sleep 2
    
    check_ports
    
    echo ""
    echo -e "${GREEN}🎯 所有服务已停止${NC}"
    echo -e "${BLUE}💡 要重新启动服务，请运行: ${YELLOW}./dev-start.sh${NC}"
}

# 执行主函数
main "$@"
