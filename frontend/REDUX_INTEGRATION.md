# Redux状态管理集成

本项目已成功集成Redux Toolkit进行状态管理，提供了集中化的状态管理和可预测的状态更新。

## 项目结构

```
src/
├── store/
│   ├── index.ts              # Store配置
│   ├── hooks.ts              # 类型化的Redux hooks
│   └── slices/
│       ├── authSlice.ts      # 认证状态管理
│       ├── ticketsSlice.ts  # 票据状态管理
│       └── employeesSlice.ts # 员工状态管理
├── components/
│   └── AuthInitializer.tsx  # 认证状态初始化组件
└── ...
```

## 状态切片说明

### 1. 认证状态 (authSlice)

- **状态**: 用户信息、认证状态、加载状态、错误信息
- **异步操作**:
  - `loginUser` - 用户登录
  - `registerUser` - 用户注册
  - `logoutUser` - 用户登出
  - `initializeAuth` - 初始化认证状态

### 2. 票据状态 (ticketsSlice)

- **状态**: 票据列表、加载状态、错误信息
- **异步操作**:
  - `fetchTickets` - 获取票据列表
  - `createNewTicket` - 创建新票据
  - `approveTicketAction` - 批准票据
  - `denyTicketAction` - 拒绝票据
  - `deleteTicketAction` - 删除票据

### 3. 员工状态 (employeesSlice)

- **状态**: 员工列表、加载状态、错误信息
- **异步操作**:
  - `fetchEmployees` - 获取员工列表
  - `suspendEmployeeAction` - 暂停员工
  - `activateEmployeeAction` - 激活员工

## 使用方法

### 在组件中使用Redux状态

```tsx
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { loginUser, clearError } from '../store/slices/authSlice';

function LoginComponent() {
  const dispatch = useAppDispatch();
  const { loading, error, isAuthenticated } = useAppSelector(
    state => state.auth
  );

  const handleLogin = credentials => {
    dispatch(loginUser(credentials));
  };

  // 组件逻辑...
}
```

### 类型安全

项目使用TypeScript提供完整的类型安全：

- `RootState` - 整个应用的状态类型
- `AppDispatch` - dispatch函数的类型
- `useAppSelector` - 类型化的useSelector hook
- `useAppDispatch` - 类型化的useDispatch hook

## 特性

1. **集中化状态管理**: 所有应用状态集中在Redux store中
2. **异步操作处理**: 使用createAsyncThunk处理API调用
3. **错误处理**: 统一的错误状态管理
4. **加载状态**: 为异步操作提供加载状态
5. **类型安全**: 完整的TypeScript支持
6. **自动认证**: HTTP拦截器自动处理401错误并登出用户
7. **状态持久化**: 认证状态在localStorage中持久化

## 优势

- **可预测性**: 状态更新遵循严格的规则
- **调试友好**: Redux DevTools支持
- **测试友好**: 纯函数reducer易于测试
- **性能优化**: 避免不必要的重新渲染
- **代码组织**: 清晰的状态管理结构
