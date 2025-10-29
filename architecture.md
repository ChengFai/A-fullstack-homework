## 报销系统整体架构

### 目标
- 支持两类用户：员工（Employee）、雇主（Employer）
- 功能：登录/注册、票据增删改查、雇主审批/拒绝票据、雇主停用/恢复员工
- 本阶段采用文件存储作为临时方案，后续可无缝切换 PostgreSQL

### 技术栈
- 后端：FastAPI（async）+ Pydantic +（后续：SQLAlchemy + asyncpg + PostgreSQL）
- 前端：TypeScript + React + Vite + React Router + TailwindCSS（可选 Redux）
- 包管理：后端 Astral UV；前端 PNPM

### 目录结构
```
README.md
ARCHITECTURE.md
frontend/
  package.json
  vite.config.ts
  index.html
  tailwind.config.ts
  postcss.config.js
  src/
    main.tsx
    App.tsx
    routes/
      LoginPage.tsx
      TicketListPage.tsx
      EmployeeListPage.tsx
    services/
      http.ts
      auth.ts
      tickets.ts
      employees.ts
    types.ts
    index.css
backend/
  pyproject.toml
  uv.lock (运行后生成)
  src/
    app/
      main.py
      storage.py
      routers/
        auth.py
        tickets.py
        employees.py
      schemas/
        auth.py
        user.py
        ticket.py
        common.py
      security/
        jwt.py
        passwords.py
        dependencies.py
```

### 核心数据模型（阶段性：文件存储；目标：DB）
- User
  - id: uuid
  - email: string（唯一）
  - username: string
  - role: 'employee' | 'employer'
  - passwordHash: string
  - isSuspended: boolean
  - createdAt, updatedAt
- Ticket
  - id: uuid
  - userId: uuid
  - spentAt: datetime
  - amount: number
  - currency: string
  - description?: string
  - link?: string
  - status: 'pending' | 'approved' | 'denied'
  - isSoftDeleted: boolean
  - createdAt, updatedAt

### API 概览
- Auth
  - POST /auth/login-or-register
  - GET /auth/me
- Tickets
  - GET /tickets
  - POST /tickets
  - GET /tickets/{id}
  - PUT /tickets/{id}
  - DELETE /tickets/{id}
  - POST /tickets/{id}/approve
  - POST /tickets/{id}/deny
- Employees（仅雇主）
  - GET /employees
  - POST /employees/{id}/suspend
  - POST /employees/{id}/activate

### 鉴权 & 授权
- JWT Bearer 认证（开发阶段使用简单密钥，生产换环境变量）
- 角色守卫：
  - 员工：可管理自己的票据；仅 pending 可编辑/删除
  - 雇主：可查看全部票据并审批；可停用/恢复员工
- 被停用用户不可登录；其票据在列表中隐藏（通过联查或过滤）

### 并发与一致性
- FastAPI 异步端点
- 文件存储阶段使用 asyncio.Lock 保护共享状态和文件操作
- 审批操作具备幂等校验
- 数据自动持久化到 JSON 文件

### 迁移到数据库的路径
- 将 `storage.py` 的文件存储仓库替换为仓储接口 + SQLAlchemy 实现
- 在服务层保持业务不变，逐步引入事务与行级锁
- 当前文件存储方案：`data/users.json` 和 `data/tickets.json`

### 前端路由
- /login
- /tickets
- /employees（雇主）

### UI 要点
- 表格 + 筛选/分页（前期可前端分页）
- 登录/注册合一交互：新用户需选择角色与用户名


