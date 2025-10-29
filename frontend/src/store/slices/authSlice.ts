import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { login, register, checkUserExists as checkUserExistsService, validateToken } from '../../services/auth';

export interface User {
  id: string;
  email: string;
  username: string;
  role: 'employee' | 'employer';
  is_suspended?: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  userExists: boolean | null;
  checkingUser: boolean;
  showSuspensionAlert: boolean;
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
  error: null,
  userExists: null,
  checkingUser: false,
  showSuspensionAlert: false,
};

// 异步thunk：登录
export const loginUser = createAsyncThunk(
  'auth/login',
  async (
    credentials: { email: string; password: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await login(credentials);
      localStorage.setItem('token', response.token);
      localStorage.setItem('role', response.user.role);
      return response;
    } catch (error: any) {
      // 检查是否是账户停用错误
      // 注意：HTTP拦截器会标准化错误，所以我们需要检查message字段
      if ((error?.status === 403 || error?.response?.status === 403) && 
          (error?.message?.includes('停用') || error?.response?.data?.detail?.includes('停用'))) {
        return rejectWithValue({
          type: 'suspension',
          message: error?.message || error?.response?.data?.detail || '您的账户已被停用，请联系管理员'
        });
      }
      return rejectWithValue(
        error?.message || error?.response?.data?.detail || error?.message || '登录失败'
      );
    }
  }
);

// 异步thunk：注册
export const registerUser = createAsyncThunk(
  'auth/register',
  async (
    userData: {
      email: string;
      password: string;
      role: 'employee' | 'employer';
      username: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await register(userData);
      localStorage.setItem('token', response.token);
      localStorage.setItem('role', response.user.role);
      return response;
    } catch (error: any) {
      return rejectWithValue(
        error?.response?.data?.detail || error?.message || '注册失败'
      );
    }
  }
);

// 异步thunk：检查用户是否存在
export const checkUserExists = createAsyncThunk(
  'auth/checkUserExists',
  async (email: string, { rejectWithValue }) => {
    try {
      const response = await checkUserExistsService(email);
      return response.exists;
    } catch (error: any) {
      return rejectWithValue(
        error?.response?.data?.detail || error?.message || '检查用户失败'
      );
    }
  }
);

// 异步thunk：登出
export const logoutUser = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      localStorage.clear();
      return null;
    } catch (error: any) {
      return rejectWithValue(error?.message || '登出失败');
    }
  }
);

// 异步thunk：初始化用户信息
export const initializeAuth = createAsyncThunk(
  'auth/initialize',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        return null;
      }

      // 验证token有效性并获取用户信息
      const response = await validateToken();
      
      // 如果用户被暂停，清除认证状态
      if (response.user.is_suspended) {
        localStorage.clear();
        return null;
      }

      return response;
    } catch (error: any) {
      // Token无效，清除本地存储
      localStorage.clear();
      return rejectWithValue(error?.message || 'Token验证失败');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: state => {
      state.error = null;
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    clearUserExists: state => {
      state.userExists = null;
    },
    closeSuspensionAlert: state => {
      state.showSuspensionAlert = false;
    },
  },
  extraReducers: builder => {
    builder
      // 登录
      .addCase(loginUser.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        const payload = action.payload as any;
        if (payload?.type === 'suspension') {
          state.showSuspensionAlert = true;
          state.error = null; // 不显示普通错误，而是显示停用提示
        } else {
          state.error = payload as string;
          state.showSuspensionAlert = false;
        }
      })
      // 注册
      .addCase(registerUser.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 登出
      .addCase(logoutUser.fulfilled, state => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = null;
      })
      // 初始化认证
      .addCase(initializeAuth.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(initializeAuth.fulfilled, (state, action) => {
        state.loading = false;
        if (action.payload) {
          state.user = action.payload.user;
          state.token = action.payload.token;
          state.isAuthenticated = true;
          state.error = null;
        } else {
          state.user = null;
          state.token = null;
          state.isAuthenticated = false;
        }
      })
      .addCase(initializeAuth.rejected, (state, action) => {
        state.loading = false;
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      })
      // 检查用户是否存在
      .addCase(checkUserExists.pending, state => {
        state.checkingUser = true;
        state.error = null;
      })
      .addCase(checkUserExists.fulfilled, (state, action) => {
        state.checkingUser = false;
        state.userExists = action.payload;
        state.error = null;
      })
      .addCase(checkUserExists.rejected, (state, action) => {
        state.checkingUser = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, setUser, clearUserExists, closeSuspensionAlert } = authSlice.actions;
export default authSlice.reducer;
