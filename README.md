# Expense Tracker 费用跟踪系统

基于 `goal.md` 要求实现的费用跟踪系统，支持员工和雇主两种角色的报销管理。

## 功能特性

- **用户认证**: 独立的登录和注册接口，JWT token认证
- **角色管理**: 员工和雇主两种角色，不同权限
- **票据管理**: 创建、更新、删除、审批报销票据
- **员工管理**: 雇主可以停用/激活员工账户
- **软删除**: 被停用员工的票据会被隐藏但保留在数据库中

## 技术栈

### 后端
- **Python**: FastAPI + Uvicorn
- **认证**: JWT + Passlib (bcrypt)
- **包管理**: Astral UV
- **数据存储**: 内存存储（可扩展至数据库）

### 前端
- **框架**: React + TypeScript
- **构建工具**: Vite + ESBuild
- **样式**: TailwindCSS
- **路由**: React Router
- **包管理**: PNPM
- **HTTP客户端**: Axios

## 快速开始

### 环境要求

#### 本地开发模式
- Python 3.10+
- Node.js 16+
- npm (或 pnpm)
- Astral UV (Python包管理器)

#### Docker模式
- Docker 20.10+
- Docker Compose 2.0+

### 方式一：一键启动（推荐）

使用我们提供的一键启动脚本，支持本地开发模式和Docker模式：

#### 本地开发模式（默认）
```bash
# 一键启动前后端服务（本地开发模式）
./dev-start.sh
# 或
./dev-start.sh --local

# 停止所有服务
./dev-stop.sh
```

#### Docker模式
```bash
# 使用Docker启动所有服务
./dev-start.sh --docker

# 停止Docker服务
docker-compose down
```

#### 脚本功能说明

**本地开发模式**会自动：
- 检查环境要求（Node.js、Python、uv）
- 安装前端和后端依赖
- 启动后端服务（端口 8000）
- 启动前端服务（端口 5173）
- 等待服务就绪并显示访问地址

**Docker模式**会自动：
- 检查Docker和Docker Compose环境
- 验证Docker配置文件完整性
- 构建Docker镜像
- 启动所有服务（数据库、后端、前端）
- 等待所有服务就绪并显示访问地址

#### 访问地址

**本地开发模式**：
- 前端：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

**Docker模式**：
- 前端：http://localhost
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs
- 数据库：localhost:5432

### 方式二：手动启动

#### 1. 安装 Astral UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. 启动后端服务

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
uv venv

# 安装依赖
uv pip install -e .

# 启动服务
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 `http://localhost:8000` 启动，API文档可在 `http://localhost:8000/docs` 查看。

#### 3. 启动前端服务

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 `http://localhost:5173` 启动。

## 使用指南

### 用户注册

1. 访问 `http://localhost:5173`
2. 点击"注册"按钮
3. 填写邮箱、用户名、选择角色（员工/雇主）、设置密码
4. 注册成功后自动登录

### 用户登录

1. 访问 `http://localhost:5173`
2. 点击"登录"按钮
3. 输入邮箱和密码
4. 登录成功后跳转到票据管理页面

### 员工功能

- **查看票据**: 只能看到自己创建的票据
- **创建票据**: 添加新的报销记录
- **编辑票据**: 修改待审批状态的票据
- **删除票据**: 删除待审批状态的票据

### 雇主功能

- **查看所有票据**: 可以看到所有员工的票据
- **审批票据**: 批准或拒绝员工的报销申请
- **员工管理**: 停用或激活员工账户
- **员工列表**: 查看所有员工状态

## API 接口文档

### 认证接口

#### 用户登录
- **URL**: `POST /auth/login`
- **描述**: 用户登录获取JWT令牌
- **请求体**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **响应**:
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "username",
      "role": "employee"
    }
  }
  ```

#### 用户注册
- **URL**: `POST /auth/register`
- **描述**: 新用户注册
- **请求体**:
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "password": "password123",
    "role": "employee"
  }
  ```
- **响应**: 同登录响应

#### 获取当前用户信息
- **URL**: `GET /auth/me`
- **描述**: 获取当前登录用户信息
- **请求头**: `Authorization: Bearer <token>`
- **响应**:
  ```json
  {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "role": "employee",
    "is_suspended": false,
    "created_at": "2024-01-01T00:00:00Z"
  }
  ```

### 票据接口

#### 获取票据列表
- **URL**: `GET /tickets/`
- **描述**: 获取票据列表（员工只能看到自己的，雇主可以看到所有）
- **请求头**: `Authorization: Bearer <token>`
- **查询参数**:
  - `status` (可选): 票据状态过滤 (pending/approved/denied)
  - `limit` (可选): 每页数量，默认20
  - `offset` (可选): 偏移量，默认0
- **响应**:
  ```json
  {
    "tickets": [
      {
        "id": "uuid",
        "spent_at": "2024-01-01T00:00:00Z",
        "amount": 100.50,
        "currency": "USD",
        "description": "办公用品",
        "link": "https://example.com/receipt",
        "status": "pending",
        "user_id": "uuid",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0
  }
  ```

#### 创建票据
- **URL**: `POST /tickets/`
- **描述**: 创建新的报销票据
- **请求头**: `Authorization: Bearer <token>`
- **请求体**:
  ```json
  {
    "spent_at": "2024-01-01T00:00:00Z",
    "amount": 100.50,
    "currency": "USD",
    "description": "办公用品",
    "link": "https://example.com/receipt"
  }
  ```
- **响应**: 创建的票据信息

#### 获取单个票据
- **URL**: `GET /tickets/{ticket_id}`
- **描述**: 获取指定票据详情
- **请求头**: `Authorization: Bearer <token>`
- **响应**: 票据详细信息

#### 更新票据
- **URL**: `PUT /tickets/{ticket_id}`
- **描述**: 更新票据信息（只能更新待审批状态的票据）
- **请求头**: `Authorization: Bearer <token>`
- **请求体**: 同创建票据

#### 删除票据
- **URL**: `DELETE /tickets/{ticket_id}`
- **描述**: 删除票据（只能删除待审批状态的票据）
- **请求头**: `Authorization: Bearer <token>`

#### 批准票据
- **URL**: `POST /tickets/{ticket_id}/approve`
- **描述**: 批准票据（仅雇主可用）
- **请求头**: `Authorization: Bearer <token>`

#### 拒绝票据
- **URL**: `POST /tickets/{ticket_id}/deny`
- **描述**: 拒绝票据（仅雇主可用）
- **请求头**: `Authorization: Bearer <token>`

### 员工管理接口

#### 获取员工列表
- **URL**: `GET /employees/`
- **描述**: 获取所有员工列表（仅雇主可用）
- **请求头**: `Authorization: Bearer <token>`
- **响应**:
  ```json
  {
    "employees": [
      {
        "id": "uuid",
        "email": "employee@example.com",
        "username": "employee1",
        "role": "employee",
        "is_suspended": false,
        "created_at": "2024-01-01T00:00:00Z",
        "ticket_count": 5
      }
    ],
    "total": 1
  }
  ```

#### 暂停员工
- **URL**: `POST /employees/{user_id}/suspend`
- **描述**: 暂停员工账户（仅雇主可用）
- **请求头**: `Authorization: Bearer <token>`

#### 激活员工
- **URL**: `POST /employees/{user_id}/activate`
- **描述**: 激活员工账户（仅雇主可用）
- **请求头**: `Authorization: Bearer <token>`

### 错误响应格式

所有API错误都遵循统一格式：

```json
{
  "detail": "错误描述信息",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

常见错误代码：
- `INVALID_CREDENTIALS`: 用户名或密码错误
- `USER_NOT_FOUND`: 用户不存在
- `USER_SUSPENDED`: 用户已被暂停
- `INSUFFICIENT_PERMISSIONS`: 权限不足
- `TICKET_NOT_FOUND`: 票据不存在
- `INVALID_TICKET_STATUS`: 票据状态无效
- `VALIDATION_ERROR`: 数据验证错误

## 开发说明

### 后端开发

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
source .venv/bin/activate

# 安装开发依赖
uv pip install -e ".[dev]"

# 运行服务
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
# 进入前端目录
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 代码格式化
pnpm format

# 构建生产版本
pnpm build
```

### 项目结构

```
├── README.md
├── backend/
│   ├── pyproject.toml
│   ├── README.md
│   └── src/
│       └── app/
│           ├── main.py
│           ├── routers/
│           ├── schemas/
│           ├── security/
│           └── storage.py
└── frontend/
    ├── package.json
    ├── src/
    │   ├── App.tsx
    │   ├── main.tsx
    │   ├── routes/
    │   └── services/
    └── index.html
```

## 环境配置

### 环境变量

#### 后端环境变量

创建 `backend/.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:password123@localhost:5432/expense_tracker

# JWT配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
DEBUG=true
LOG_LEVEL=INFO
```

#### 前端环境变量

创建 `frontend/.env` 文件：

```env
# API配置
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=10000

# 应用配置
VITE_APP_NAME=Expense Tracker
VITE_APP_VERSION=1.0.0
```

### 生产环境配置

#### Docker环境变量

创建 `.env` 文件：

```env
# 数据库配置
POSTGRES_DB=expense_tracker
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql+asyncpg://postgres:your_secure_password_here@postgres:5432/expense_tracker

# 后端配置
SECRET_KEY=your_production_secret_key_here
DEBUG=false
LOG_LEVEL=WARNING

# 前端配置
REACT_APP_API_URL=http://your-domain.com/api
```

## 部署指南

### Docker部署（推荐）

#### 1. 准备环境

```bash
# 确保Docker和Docker Compose已安装
docker --version
docker-compose --version

# 克隆项目
git clone <repository-url>
cd A-fullstack-homework
```

#### 2. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env

# 编辑环境变量
nano .env
```

#### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 4. 访问应用

- **前端应用**: http://localhost
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **数据库**: localhost:5432

### 手动部署

#### 1. 数据库设置

```bash
# 安装PostgreSQL
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库
sudo -u postgres psql
CREATE DATABASE expense_tracker;
CREATE USER postgres WITH PASSWORD 'password123';
GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO postgres;
\q
```

#### 2. 后端部署

```bash
cd backend

# 安装依赖
uv venv
uv pip install -e .

# 设置环境变量
export DATABASE_URL="postgresql+asyncpg://postgres:password123@localhost:5432/expense_tracker"
export SECRET_KEY="your-secret-key"

# 启动服务
uv run uvicorn src.app.main:app --host 0.0.0.0 --port 8000
```

#### 3. 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 使用nginx或其他web服务器部署dist目录
```

### 云平台部署

#### AWS EC2部署

1. **启动EC2实例**
   - 选择Ubuntu 20.04 LTS
   - 配置安全组（开放80、443、8000端口）

2. **安装Docker**
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **部署应用**
   ```bash
   git clone <repository-url>
   cd A-fullstack-homework
   docker-compose up -d
   ```

#### Google Cloud Run部署

1. **构建镜像**
   ```bash
   # 构建后端镜像
   docker build -f Dockerfile.backend -t gcr.io/PROJECT_ID/expense-tracker-backend .
   
   # 构建前端镜像
   docker build -f Dockerfile.frontend -t gcr.io/PROJECT_ID/expense-tracker-frontend .
   ```

2. **推送镜像**
   ```bash
   docker push gcr.io/PROJECT_ID/expense-tracker-backend
   docker push gcr.io/PROJECT_ID/expense-tracker-frontend
   ```

3. **部署服务**
   ```bash
   gcloud run deploy expense-tracker-backend --image gcr.io/PROJECT_ID/expense-tracker-backend
   gcloud run deploy expense-tracker-frontend --image gcr.io/PROJECT_ID/expense-tracker-frontend
   ```

## 测试

### 运行测试

#### 后端测试

```bash
cd backend

# 安装测试依赖
uv pip install -e ".[dev]"

# 运行所有测试
python run_tests.py all

# 运行单元测试
python run_tests.py unit

# 运行集成测试
python run_tests.py integration

# 生成覆盖率报告
python run_tests.py coverage
```

#### 前端测试

```bash
cd frontend

# 运行测试
npm test

# 运行测试并生成覆盖率报告
npm run test:coverage
```

### 代码质量检查

#### 后端代码格式化

```bash
cd backend

# 格式化代码
uv run black .

# 检查代码格式
uv run black --check .

# 排序导入
uv run isort .

# 检查导入排序
uv run isort --check-only .
```

#### 前端代码格式化

```bash
cd frontend

# 格式化代码
npm run format

# 检查代码格式
npm run format:check

# 运行lint检查
npm run lint
```

## 监控和维护

### 日志管理

#### 查看日志

```bash
# Docker环境
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# 本地环境
# 后端日志在控制台输出
# 前端日志在浏览器开发者工具中查看
```

#### 日志配置

后端日志配置在 `backend/src/app/main.py` 中：

```python
import logging

# 配置日志级别
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### 性能监控

#### 数据库性能

```bash
# 查看数据库连接
docker-compose exec postgres psql -U postgres -d expense_tracker -c "SELECT * FROM pg_stat_activity;"

# 查看慢查询
docker-compose exec postgres psql -U postgres -d expense_tracker -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

#### API性能

访问 `http://localhost:8000/metrics` 查看API性能指标（如果启用了监控）。

### 备份和恢复

#### 数据库备份

```bash
# 创建备份
docker-compose exec postgres pg_dump -U postgres expense_tracker > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复备份
docker-compose exec -T postgres psql -U postgres expense_tracker < backup_20240101_120000.sql
```

#### 应用备份

```bash
# 备份整个项目
tar -czf expense_tracker_backup_$(date +%Y%m%d_%H%M%S).tar.gz .

# 备份数据库数据卷
docker run --rm -v expense_tracker_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data_backup.tar.gz -C /data .
```

## Troubleshooting

### 常见问题

#### 1. 数据库连接失败

**症状**: 后端启动时出现数据库连接错误

**解决方案**:
```bash
# 检查数据库是否运行
docker-compose ps postgres

# 检查数据库连接
docker-compose exec postgres psql -U postgres -d expense_tracker -c "SELECT version();"

# 重启数据库
docker-compose restart postgres
```

#### 2. 前端无法访问后端API

**症状**: 前端页面显示网络错误

**解决方案**:
```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查CORS配置
# 确保后端CORS配置允许前端域名

# 检查nginx代理配置
docker-compose logs frontend
```

#### 3. JWT令牌验证失败

**症状**: 用户登录后无法访问受保护的路由

**解决方案**:
```bash
# 检查SECRET_KEY配置
echo $SECRET_KEY

# 检查令牌格式
# 确保Authorization头格式为: Bearer <token>

# 检查令牌过期时间
# 默认30分钟，可在环境变量中调整
```

#### 4. 端口冲突

**症状**: 服务启动失败，提示端口被占用

**解决方案**:
```bash
# 检查端口占用
lsof -i :8000  # 后端端口
lsof -i :5173  # 前端端口
lsof -i :5432  # 数据库端口

# 停止占用端口的进程
sudo kill -9 <PID>

# 或修改docker-compose.yml中的端口映射
```

#### 5. 权限问题

**症状**: 文件操作被拒绝

**解决方案**:
```bash
# 给脚本添加执行权限
chmod +x dev-start.sh dev-stop.sh

# 修复Docker权限问题
sudo chown -R $USER:$USER .

# 重新构建Docker镜像
docker-compose build --no-cache
```

### 调试技巧

#### 1. 启用详细日志

```bash
# 后端调试模式
export DEBUG=true
export LOG_LEVEL=DEBUG

# 前端调试模式
export NODE_ENV=development
```

#### 2. 检查网络连接

```bash
# 测试容器间网络
docker-compose exec backend ping postgres
docker-compose exec frontend ping backend

# 检查DNS解析
docker-compose exec backend nslookup postgres
```

#### 3. 查看资源使用

```bash
# 查看容器资源使用
docker stats

# 查看系统资源
top
htop
```

### 性能优化

#### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_tickets_user_id ON tickets(user_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);

-- 分析查询性能
EXPLAIN ANALYZE SELECT * FROM tickets WHERE user_id = 'uuid';
```

#### 2. 应用优化

```bash
# 启用gzip压缩
# 在nginx配置中添加gzip设置

# 启用缓存
# 配置适当的HTTP缓存头

# 优化镜像大小
# 使用多阶段构建和Alpine基础镜像
```

### 安全考虑

#### 1. 生产环境安全

- 使用强密码和随机SECRET_KEY
- 启用HTTPS
- 配置防火墙规则
- 定期更新依赖包
- 启用数据库SSL连接

#### 2. 数据保护

- 定期备份数据库
- 加密敏感数据
- 实施访问控制
- 监控异常活动

## 贡献指南

### 开发流程

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 运行测试
5. 创建Pull Request

### 代码规范

- 后端使用Black格式化
- 前端使用Prettier格式化
- 提交信息使用约定式提交格式
- 确保测试覆盖率≥80%

### 问题报告

使用GitHub Issues报告问题，包含：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息

