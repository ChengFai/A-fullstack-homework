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

## API 接口

### 认证接口

- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册
- `GET /auth/me` - 获取当前用户信息

### 票据接口

- `GET /tickets/` - 获取票据列表
- `POST /tickets/` - 创建票据
- `GET /tickets/{id}` - 获取单个票据
- `PUT /tickets/{id}` - 更新票据
- `DELETE /tickets/{id}` - 删除票据
- `POST /tickets/{id}/approve` - 批准票据
- `POST /tickets/{id}/deny` - 拒绝票据

### 员工管理接口

- `GET /employees/` - 获取员工列表
- `POST /employees/{id}/suspend` - 停用员工
- `POST /employees/{id}/activate` - 激活员工

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

## Troubleshooting

### 一键启动脚本问题

1. **脚本权限问题**
   ```bash
   # 给脚本添加执行权限
   chmod +x dev-start.sh dev-stop.sh
   ```

2. **服务无法停止**
   ```bash
   # 使用停止脚本
   ./dev-stop.sh
   
   # 或者手动停止所有相关进程
   pkill -f uvicorn
   pkill -f vite
   ```

3. **端口被占用**
   ```bash
   # 检查端口占用
   lsof -i :8000  # 后端端口
   lsof -i :5173  # 前端端口
   
   # 使用停止脚本清理
   ./dev-stop.sh
   ```

### 后端问题

1. **UV 命令未找到**
   ```bash
   # 重新安装 UV
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env
   ```

2. **依赖安装失败**
   ```bash
   # 清理并重新安装
   cd backend
   rm -rf .venv
   uv venv
   uv pip install -e .
   ```

### 前端问题

1. **npm 未安装**
   ```bash
   # 安装 Node.js 和 npm
   # 访问 https://nodejs.org/ 下载安装
   ```

2. **依赖安装失败**
   ```bash
   # 清理并重新安装
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

