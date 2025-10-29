# 后端测试框架文档

## 概述

本项目为后端API提供了完整的单元测试和集成测试框架，使用pytest作为测试运行器，确保代码质量和功能正确性。

## 测试结构

```
backend/
├── tests/
│   ├── unit/                    # 单元测试
│   │   ├── test_security.py     # 安全模块测试
│   │   └── test_storage.py      # 存储模块测试
│   ├── integration/             # 集成测试
│   │   ├── test_auth.py         # 认证API测试
│   │   ├── test_tickets.py      # 票据API测试
│   │   └── test_employees.py    # 员工管理API测试
│   └── fixtures/                 # 测试fixtures
│       └── conftest.py          # 共享测试配置
├── pytest.ini                  # pytest配置
└── run_tests.py                # 测试运行脚本
```

## 测试类型

### 单元测试 (Unit Tests)

测试独立的函数和类，不依赖外部资源：

- **安全模块测试** (`test_security.py`)
  - 密码哈希和验证
  - JWT令牌创建和验证
  - 安全常量和配置

- **存储模块测试** (`test_storage.py`)
  - User和Ticket模型
  - FileDB数据库操作
  - 数据序列化和反序列化

### 集成测试 (Integration Tests)

测试API端点的完整功能，包括认证、授权和业务逻辑：

- **认证API测试** (`test_auth.py`)
  - 用户注册和登录
  - JWT令牌生成
  - 用户信息获取
  - 错误处理

- **票据API测试** (`test_tickets.py`)
  - 票据CRUD操作
  - 权限控制（员工vs雇主）
  - 状态管理（pending/approved/denied）
  - 软删除功能

- **员工管理API测试** (`test_employees.py`)
  - 员工列表获取
  - 员工暂停和激活
  - 权限验证

## 运行测试

### 安装测试依赖

```bash
cd backend
python run_tests.py install
```

### 运行特定测试

```bash
# 运行单元测试
python run_tests.py unit

# 运行集成测试
python run_tests.py integration

# 运行所有测试
python run_tests.py all

# 快速测试（遇到失败立即停止）
python run_tests.py fast
```

### 生成覆盖率报告

```bash
# 运行测试并生成覆盖率报告
python run_tests.py coverage
```

覆盖率报告将生成在 `htmlcov/index.html`，可以在浏览器中查看详细的覆盖率信息。

### 直接使用pytest

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/unit/test_security.py

# 运行特定测试类
pytest tests/integration/test_auth.py::TestAuthEndpoints

# 运行特定测试方法
pytest tests/unit/test_security.py::TestPasswordHashing::test_hash_password_returns_string

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

## 测试配置

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    -v
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

### 测试标记

- `@pytest.mark.unit`: 单元测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.slow`: 慢速测试

## 测试Fixtures

### 数据库相关

- `clean_db`: 清理数据库，确保每个测试都有干净的环境
- `test_user_employee`: 创建测试员工用户
- `test_user_employer`: 创建测试雇主用户
- `test_ticket`: 创建测试票据

### 认证相关

- `auth_headers_employee`: 员工用户的认证头
- `auth_headers_employer`: 雇主用户的认证头
- `invalid_auth_headers`: 无效的认证头

### 测试数据

- `sample_login_data`: 示例登录数据
- `sample_register_data`: 示例注册数据
- `sample_ticket_data`: 示例票据数据

## 测试最佳实践

### 1. 测试隔离

每个测试都使用 `clean_db` fixture确保数据库状态干净，避免测试间的相互影响。

### 2. 异步测试

使用 `pytest-asyncio` 支持异步测试，所有数据库操作和API调用都是异步的。

### 3. 错误测试

每个功能都包含正常情况和各种错误情况的测试，确保错误处理正确。

### 4. 权限测试

集成测试验证了不同角色（员工/雇主）的权限控制是否正确。

### 5. 数据验证

测试验证API响应的数据结构、字段类型和业务逻辑正确性。

## 持续集成

### GitHub Actions示例

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10
    - name: Install dependencies
      run: |
        cd backend
        python run_tests.py install
    - name: Run tests
      run: |
        cd backend
        python run_tests.py coverage
```

## 测试覆盖率目标

- 整体覆盖率: ≥ 80%
- 关键模块覆盖率: ≥ 90%
- 新增代码覆盖率: ≥ 95%

## 故障排除

### 常见问题

1. **导入错误**: 确保 `src` 目录在Python路径中
2. **数据库锁定**: 确保测试使用独立的临时数据库
3. **异步测试失败**: 检查是否正确使用 `async_client` fixture
4. **认证失败**: 验证JWT令牌生成和验证逻辑

### 调试技巧

```bash
# 运行单个测试并显示详细输出
pytest tests/unit/test_security.py::TestPasswordHashing::test_hash_password_returns_string -v -s

# 在测试失败时进入调试器
pytest tests/ --pdb

# 显示测试覆盖率中未覆盖的行
pytest tests/ --cov=src --cov-report=term-missing
```

## 扩展测试

### 添加新测试

1. 在相应的测试文件中添加新的测试方法
2. 使用现有的fixtures或创建新的fixtures
3. 确保测试覆盖正常情况和错误情况
4. 运行测试验证功能正确性

### 性能测试

可以考虑添加性能测试来验证API响应时间：

```python
@pytest.mark.slow
async def test_api_response_time(self, async_client):
    start_time = time.time()
    response = await async_client.get("/tickets/", headers=auth_headers)
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # 响应时间应小于1秒
```

这个测试框架为后端API提供了全面的测试覆盖，确保代码质量和功能正确性。
