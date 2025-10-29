# 开发环境一键启动脚本使用说明

## 概述

为了方便开发，我们提供了两个脚本来自动化前后端服务的启动和停止：

- `dev-start.sh` - 一键启动前后端服务
- `dev-stop.sh` - 一键停止所有服务

## 使用方法

### 启动服务

```bash
./dev-start.sh
```

这个脚本会：
1. 检查环境要求（Node.js、Python、uv）
2. 自动安装前端和后端依赖
3. 启动后端服务（端口 8000）
4. 启动前端服务（端口 5173）
5. 等待服务就绪并显示访问地址

### 停止服务

```bash
./dev-stop.sh
```

这个脚本会：
1. 停止所有后端服务进程
2. 停止所有前端服务进程
3. 清理相关进程
4. 检查端口释放情况

## 服务地址

启动成功后，你可以访问：

- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 注意事项

1. **首次运行**：脚本会自动安装所有依赖，可能需要几分钟时间
2. **端口占用**：确保端口 8000 和 5173 没有被其他程序占用
3. **环境要求**：需要安装 Node.js、Python 3.10+ 和 uv
4. **停止服务**：使用 Ctrl+C 或运行 `./dev-stop.sh` 来停止服务

## 故障排除

### 权限问题
```bash
chmod +x dev-start.sh dev-stop.sh
```

### 端口被占用
```bash
# 检查端口占用
lsof -i :8000
lsof -i :5173

# 使用停止脚本清理
./dev-stop.sh
```

### 依赖安装失败
```bash
# 清理并重新运行
rm -rf frontend/node_modules backend/.venv
./dev-start.sh
```

## 手动启动（备选方案）

如果脚本有问题，你也可以手动启动：

### 后端
```bash
cd backend
uv venv
uv pip install -e .
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端
```bash
cd frontend
npm install
npm run dev
```
