# 测试框架使用示例

## 快速开始

### 1. 安装测试依赖
```bash
cd backend
python run_tests.py install
```

### 2. 运行测试

#### 运行所有测试
```bash
python run_tests.py all
```

#### 运行单元测试
```bash
python run_tests.py unit
```

#### 运行集成测试
```bash
python run_tests.py integration
```

#### 生成覆盖率报告
```bash
python run_tests.py coverage
```

### 3. 直接使用pytest

```bash
# 运行所有测试
uv run pytest tests/

# 运行特定测试文件
uv run pytest tests/unit/test_security.py

# 运行特定测试类
uv run pytest tests/unit/test_security.py::TestPasswordHashing

# 运行特定测试方法
uv run pytest tests/unit/test_security.py::TestPasswordHashing::test_hash_password_returns_string

# 生成覆盖率报告
uv run pytest tests/ --cov=src --cov-report=html
```

## 测试结构

```
backend/
├── tests/
│   ├── unit/                    # 单元测试
│   │   ├── test_security.py     # 安全模块测试 (27个测试)
│   │   └── test_storage.py      # 存储模块测试 (19个测试)
│   ├── integration/             # 集成测试
│   │   ├── test_auth.py         # 认证API测试 (20个测试)
│   │   ├── test_tickets.py      # 票据API测试 (30个测试)
│   │   └── test_employees.py    # 员工管理API测试 (15个测试)
│   └── fixtures/                 # 测试fixtures
│       └── conftest.py          # 共享测试配置
├── pytest.ini                  # pytest配置
├── run_tests.py                # 测试运行脚本
└── TESTING.md                  # 详细测试文档
```

## 测试覆盖的功能

### 单元测试
- **密码哈希和验证** (8个测试)
- **JWT令牌创建和验证** (10个测试)
- **User和Ticket模型** (7个测试)
- **FileDB数据库操作** (19个测试)

### 集成测试
- **用户注册和登录** (20个测试)
- **票据CRUD操作** (30个测试)
- **员工管理功能** (15个测试)
- **权限控制和错误处理**

## 测试特点

1. **完整的测试覆盖**: 包含正常情况和各种错误情况
2. **异步测试支持**: 使用pytest-asyncio支持异步API测试
3. **测试隔离**: 每个测试都有干净的数据库环境
4. **权限测试**: 验证不同角色的权限控制
5. **数据验证**: 测试API响应的数据结构和业务逻辑
6. **错误处理**: 测试各种错误情况的处理

## 运行示例

```bash
# 运行单个测试
$ uv run pytest tests/unit/test_security.py::TestPasswordHashing::test_hash_password_returns_string -v
============================= test session starts ==============================
platform darwin -- Python 3.11.4, pytest-8.4.2, pluggy-1.6.0
collecting ... collected 1 item

tests/unit/test_security.py::TestPasswordHashing::test_hash_password_returns_string PASSED [100%]

========================= 1 passed, 1 warning in 0.03s =========================
```

这个测试框架为您的后端API提供了全面的测试覆盖，确保代码质量和功能正确性。
