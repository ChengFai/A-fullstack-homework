# Docker 部署指南

本文档详细说明如何将费用跟踪系统打包成Docker镜像并进行部署。

## 项目结构

```
A-fullstack-homework/
├── backend/                 # FastAPI 后端
├── frontend/               # React 前端
├── docker-compose.yml      # Docker Compose 配置
└── Dockerfile.backend      # 后端 Dockerfile
└── Dockerfile.frontend     # 前端 Dockerfile
```

## 1. 创建 Dockerfile

### 1.1 后端 Dockerfile

在项目根目录创建 `Dockerfile.backend`：

```dockerfile
# 使用 Python 3.11 官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/pyproject.toml backend/uv.lock ./

# 安装 uv 包管理器
RUN pip install uv

# 安装 Python 依赖
RUN uv sync --frozen

# 复制源代码
COPY backend/src/ ./src/
COPY backend/data/ ./data/

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.2 前端 Dockerfile

在项目根目录创建 `Dockerfile.frontend`：

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package 文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY frontend/ ./

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物到 nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 1.3 Nginx 配置文件

创建 `nginx.conf`：

```nginx
server {
    listen 80;
    server_name localhost;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # 处理 React Router
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理到后端
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 2. 更新 Docker Compose

更新 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: expense_tracker_postgres
    environment:
      POSTGRES_DB: expense_tracker
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password123
      POSTGRES_HOST_AUTH_METHOD: trust
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: expense_tracker_backend
    environment:
      - DATABASE_URL=postgresql://postgres:password123@postgres:5432/expense_tracker
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: expense_tracker_frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

## 3. 构建和运行

### 3.1 构建所有镜像

```bash
# 在项目根目录执行
docker-compose build
```

### 3.2 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3.3 单独构建镜像

```bash
# 构建后端镜像
docker build -f Dockerfile.backend -t expense-tracker-backend .

# 构建前端镜像
docker build -f Dockerfile.frontend -t expense-tracker-frontend .
```

## 4. 生产环境部署

### 4.1 环境变量配置

创建 `.env` 文件：

```env
# 数据库配置
POSTGRES_DB=expense_tracker
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# 后端配置
DATABASE_URL=postgresql://postgres:your_secure_password@postgres:5432/expense_tracker
SECRET_KEY=your_secret_key_here

# 前端配置
REACT_APP_API_URL=http://your-domain.com/api
```

### 4.2 生产环境 Docker Compose

创建 `docker-compose.prod.yml`：

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: expense_tracker_postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    networks:
      - app-network

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: expense_tracker_backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
    restart: unless-stopped
    networks:
      - app-network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: expense_tracker_frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

### 4.3 生产环境部署命令

```bash
# 使用生产环境配置启动
docker-compose -f docker-compose.prod.yml --env-file .env up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

## 5. 常用操作

### 5.1 查看容器状态

```bash
# 查看所有容器
docker ps -a

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### 5.2 进入容器调试

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec postgres psql -U postgres -d expense_tracker
```

### 5.3 停止和清理

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 删除所有镜像
docker-compose down --rmi all
```

## 6. 故障排除

### 6.1 常见问题

1. **端口冲突**：确保端口 80、8000、5432 未被占用
2. **数据库连接失败**：检查数据库服务是否正常启动
3. **前端无法访问后端**：检查 nginx 代理配置

### 6.2 调试命令

```bash
# 检查容器健康状态
docker-compose ps

# 查看详细日志
docker-compose logs --tail=100 backend

# 检查网络连接
docker-compose exec backend ping postgres
```

## 7. 性能优化

### 7.1 多阶段构建优化

后端 Dockerfile 已使用多阶段构建，前端 Dockerfile 也使用了构建阶段分离。

### 7.2 镜像大小优化

- 使用 Alpine Linux 基础镜像
- 清理 apt 缓存
- 使用 `.dockerignore` 排除不必要的文件

### 7.3 创建 .dockerignore

在项目根目录创建 `.dockerignore`：

```
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.nyc_output
coverage
.vscode
.idea
*.log
```

## 8. 监控和维护

### 8.1 健康检查

所有服务都配置了健康检查，可以通过以下命令查看：

```bash
docker-compose ps
```

### 8.2 日志管理

```bash
# 查看实时日志
docker-compose logs -f

# 限制日志行数
docker-compose logs --tail=50 backend
```

### 8.3 备份数据库

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U postgres expense_tracker > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U postgres expense_tracker < backup.sql
```

## 9. 部署到云平台

### 9.1 Docker Hub

```bash
# 登录 Docker Hub
docker login

# 标记镜像
docker tag expense-tracker-backend your-username/expense-tracker-backend:latest
docker tag expense-tracker-frontend your-username/expense-tracker-frontend:latest

# 推送镜像
docker push your-username/expense-tracker-backend:latest
docker push your-username/expense-tracker-frontend:latest
```

### 9.2 AWS ECS / Google Cloud Run

根据云平台的具体要求，修改 Docker Compose 配置或使用相应的部署工具。

---

## 总结

通过以上步骤，您可以成功将费用跟踪系统打包成Docker镜像并部署。建议在生产环境中：

1. 使用环境变量管理敏感信息
2. 配置适当的资源限制
3. 设置日志轮转
4. 定期备份数据库
5. 监控服务健康状态

如有问题，请参考故障排除部分或查看相关日志。
