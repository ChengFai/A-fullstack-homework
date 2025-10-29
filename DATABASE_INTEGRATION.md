# PostgreSQL 数据库集成指南

## 概述

本项目已成功集成PostgreSQL数据库，使用SQLAlchemy + asyncpg作为数据库ORM和驱动。

## 安装和启动

### 1. 安装Docker

**方法A：使用Homebrew（推荐）**
```bash
# 接受Xcode许可证（需要输入密码）
sudo xcodebuild -license accept

# 安装Docker Desktop
brew install --cask docker

# 启动Docker Desktop
open -a Docker
```

**方法B：手动下载**
1. 访问 https://www.docker.com/products/docker-desktop/
2. 下载Docker Desktop for Mac
3. 安装并启动Docker Desktop

### 2. 启动PostgreSQL数据库

```bash
# 使用提供的启动脚本
./start_db.sh

# 或者手动启动
docker-compose up -d postgres
```

### 3. 测试数据库连接

```bash
# 运行数据库集成测试
python test_db_integration.py
```

### 4. 启动FastAPI服务器

```bash
cd backend
uv run uvicorn src.app.main:app --reload
```

## 数据库配置

### 连接信息
- **主机**: localhost
- **端口**: 5432
- **数据库**: expense_tracker
- **用户名**: postgres
- **密码**: password123

### 环境变量
数据库连接字符串通过环境变量 `DATABASE_URL` 配置：
```
DATABASE_URL=postgresql+asyncpg://postgres:password123@localhost:5432/expense_tracker
```

## 数据库架构

### 用户表 (users)
- `id`: UUID主键
- `email`: 邮箱（唯一索引）
- `username`: 用户名
- `role`: 角色（employee/employer）
- `password_hash`: 密码哈希
- `is_suspended`: 是否被暂停
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 票据表 (tickets)
- `id`: UUID主键
- `user_id`: 用户ID（外键）
- `spent_at`: 消费时间
- `amount`: 金额
- `currency`: 货币
- `description`: 描述
- `link`: 链接
- `status`: 状态（pending/approved/denied）
- `is_soft_deleted`: 是否软删除
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 主要变更

### 1. 依赖更新
- 添加了 `sqlalchemy>=2.0.0`
- 添加了 `asyncpg>=0.29.0`
- 添加了 `alembic>=1.13.0`

### 2. 新增文件
- `backend/src/app/database.py`: 数据库配置和连接
- `backend/src/app/models.py`: SQLAlchemy模型定义
- `backend/src/app/db_service.py`: 数据库服务层
- `docker-compose.yml`: Docker容器配置
- `backend/init.sql`: 数据库初始化脚本

### 3. 修改文件
- `backend/src/app/main.py`: 添加数据库初始化
- `backend/src/app/routers/auth.py`: 使用数据库服务
- `backend/src/app/routers/tickets.py`: 使用数据库服务
- `backend/src/app/routers/employees.py`: 使用数据库服务
- `backend/src/app/security/dependencies.py`: 使用数据库服务

## API端点

所有API端点保持不变，但现在使用PostgreSQL数据库：

- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册
- `GET /auth/me` - 获取当前用户信息
- `GET /tickets/` - 获取票据列表
- `POST /tickets/` - 创建票据
- `GET /tickets/{ticket_id}` - 获取单个票据
- `PUT /tickets/{ticket_id}` - 更新票据
- `DELETE /tickets/{ticket_id}` - 删除票据
- `POST /tickets/{ticket_id}/approve` - 批准票据
- `POST /tickets/{ticket_id}/deny` - 拒绝票据
- `GET /employees/` - 获取员工列表
- `POST /employees/{user_id}/suspend` - 暂停员工
- `POST /employees/{user_id}/activate` - 激活员工

## 故障排除

### 1. Docker相关问题
```bash
# 检查Docker状态
docker --version
docker-compose --version

# 检查容器状态
docker-compose ps

# 查看容器日志
docker-compose logs postgres
```

### 2. 数据库连接问题
```bash
# 测试数据库连接
docker-compose exec postgres psql -U postgres -d expense_tracker -c "SELECT version();"
```

### 3. 权限问题
```bash
# 确保脚本有执行权限
chmod +x start_db.sh
```

## 下一步

1. ✅ PostgreSQL数据库集成完成
2. ⏳ 完善集成测试
3. ⏳ 设置Black格式化器
4. ⏳ 实现Docker部署配置
5. ⏳ 更新项目文档
