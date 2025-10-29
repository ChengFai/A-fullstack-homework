# 路由保护功能测试

## 测试场景

### 1. 未登录用户访问受保护页面
- 访问 `/tickets` 应该重定向到 `/login`
- 访问 `/employees` 应该重定向到 `/login`

### 2. 已登录用户访问公共页面
- 访问 `/login` 应该重定向到 `/tickets`
- 访问 `/register` 应该重定向到 `/tickets`

### 3. 角色权限控制
- employee 用户访问 `/employees` 应该重定向到 `/tickets`
- employer 用户访问 `/employees` 应该正常显示

### 4. 登录后重定向
- 未登录用户直接访问 `/tickets`，登录后应该回到 `/tickets`
- 未登录用户直接访问 `/employees`，登录后应该回到 `/employees`

## 测试步骤

1. 清除浏览器localStorage
2. 直接访问 http://localhost:5173/tickets
3. 应该自动重定向到登录页面
4. 登录后应该回到tickets页面
5. 测试其他路由的保护功能
