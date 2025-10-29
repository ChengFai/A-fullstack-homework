# Docker 部署快速指南

## 🚀 快速开始

### 1. 一键启动
```bash
./start.sh
```

### 2. 测试部署
```bash
./test-docker.sh
```

### 3. 停止服务
```bash
./stop.sh
```

## 📁 文件说明

- `Dockerfile.backend` - 后端服务Docker镜像配置
- `Dockerfile.frontend` - 前端服务Docker镜像配置
- `docker-compose.yml` - 开发环境Docker Compose配置
- `docker-compose.prod.yml` - 生产环境Docker Compose配置
- `nginx.conf` - Nginx配置文件
- `env.example` - 环境变量示例文件
- `.dockerignore` - Docker构建忽略文件

## 🌐 服务访问

启动成功后，可以通过以下地址访问：

- **前端应用**: http://localhost
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **数据库**: localhost:5432

## 🔧 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 进入容器
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d expense_tracker

# 重新构建
docker-compose build --no-cache

# 完全清理
docker-compose down -v --rmi all
```

## 📋 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存
- 端口 80, 8000, 5432 可用

## 🛠️ 故障排除

如果遇到问题，请查看详细文档：`DOCKER_DEPLOYMENT.md`
