import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { login, register } from '../../services/auth';

export interface User {
  id: string;
  email: string;
  username: string;
  role: 'employee' | 'employer';
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
  error: null,
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
      return rejectWithValue(
        error?.response?.data?.detail || error?.message || '登录失败'
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
      const role = localStorage.getItem('role');

      if (token && role) {
        // 这里可以添加验证token有效性的API调用
        return { token, role };
      }
      return null;
    } catch (error: any) {
      return rejectWithValue(error?.message || '初始化认证失败');
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
        state.error = action.payload as string;
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
      .addCase(initializeAuth.fulfilled, (state, action) => {
        if (action.payload) {
          state.token = action.payload.token;
          state.isAuthenticated = true;
          // 这里可以设置用户信息，如果有API获取用户详情的话
        }
      });
  },
});

export const { clearError, setUser } = authSlice.actions;
export default authSlice.reducer;
