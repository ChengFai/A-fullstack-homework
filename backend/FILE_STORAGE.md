# 文件存储说明

## 概述

本项目目前使用文件存储作为临时数据持久化方案，替代了之前的内存存储。这样可以确保数据在服务重启后不会丢失，为将来迁移到真实数据库做好准备。

## 存储结构

```
data/
├── users.json    # 用户数据
└── tickets.json  # 票据数据
```

## 特性

### ✅ 已实现功能

- **数据持久化**: 所有数据自动保存到 JSON 文件
- **并发安全**: 使用 `asyncio.Lock()` 保护文件操作
- **自动加载**: 服务启动时自动从文件加载数据
- **错误处理**: 文件损坏时自动使用空数据，不会导致服务崩溃
- **无缝迁移**: 保持与原有 API 完全兼容

### 🔄 数据操作流程

1. **读取操作**: 直接从内存缓存读取（快速）
2. **写入操作**: 
   - 更新内存缓存
   - 立即写入文件（持久化）
   - 使用锁保证并发安全

### 📁 文件格式

**users.json**:
```json
[
  {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "role": "employee",
    "password_hash": "hashed_password",
    "is_suspended": false,
    "created_at": "2024-01-01T00:00:00+00:00",
    "updated_at": "2024-01-01T00:00:00+00:00"
  }
]
```

**tickets.json**:
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "spent_at": "2024-01-01T00:00:00+00:00",
    "amount": 100.50,
    "currency": "CNY",
    "description": "描述",
    "link": "https://example.com",
    "status": "pending",
    "is_soft_deleted": false,
    "created_at": "2024-01-01T00:00:00+00:00",
    "updated_at": "2024-01-01T00:00:00+00:00"
  }
]
```

## 使用说明

### 启动服务
```bash
# 数据目录会自动创建
cd backend
uvicorn src.app.main:app --reload
```

### 数据备份
```bash
# 备份数据文件
cp -r data/ backup/
```

### 数据恢复
```bash
# 恢复数据文件
cp -r backup/ data/
```

## 迁移到数据库

当准备使用真实数据库时，只需要：

1. 修改 `storage.py` 中的 `FileDB` 类
2. 实现相同的接口方法
3. 保持 API 层不变

```python
# 当前
db = FileDB()

# 未来
db = PostgreSQLDB()  # 或其他数据库实现
```

## 注意事项

- 文件存储适合开发和小规模部署
- 生产环境建议使用专业数据库
- 数据文件建议定期备份
- 并发写入频繁时可能影响性能
