import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ProtectedRoute from '../components/ProtectedRoute';
import PublicRoute from '../components/PublicRoute';
import PermissionGuard from '../components/PermissionGuard';
import authSlice, { AuthState } from '../store/slices/authSlice';

// 测试用的模拟组件
const TestComponent = () => <div data-testid="test-component">Test Component</div>;
const LoginComponent = () => <div data-testid="login-component">Login Component</div>;

// 创建测试用的store
const createTestStore = (initialAuthState: Partial<AuthState> = {}) => {
  return configureStore({
    reducer: {
      auth: authSlice.reducer,
    },
    preloadedState: {
      auth: {
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: null,
        userExists: null,
        checkingUser: false,
        ...initialAuthState,
      },
    },
  });
};

// 测试包装器组件
const TestWrapper = ({ 
  children, 
  store, 
  initialEntries = ['/'] 
}: { 
  children: React.ReactNode; 
  store: any; 
  initialEntries?: string[] 
}) => (
  <Provider store={store}>
    <BrowserRouter>
      {children}
    </BrowserRouter>
  </Provider>
);

describe('路由保护组件测试', () => {
  describe('ProtectedRoute', () => {
    it('未认证用户应该重定向到登录页', () => {
      const store = createTestStore({
        isAuthenticated: false,
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </TestWrapper>
      );

      // 应该重定向到登录页，所以测试组件不应该显示
      expect(screen.queryByTestId('test-component')).not.toBeInTheDocument();
    });

    it('已认证用户应该能够访问受保护的页面', () => {
      const store = createTestStore({
        isAuthenticated: true,
        user: {
          id: '1',
          email: 'test@example.com',
          username: 'testuser',
          role: 'employee',
        },
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </TestWrapper>
      );

      expect(screen.getByTestId('test-component')).toBeInTheDocument();
    });

    it('被暂停的用户应该重定向到登录页', () => {
      const store = createTestStore({
        isAuthenticated: true,
        user: {
          id: '1',
          email: 'test@example.com',
          username: 'testuser',
          role: 'employee',
          is_suspended: true,
        },
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </TestWrapper>
      );

      expect(screen.queryByTestId('test-component')).not.toBeInTheDocument();
    });

    it('员工用户访问需要雇主角色的页面应该重定向', () => {
      const store = createTestStore({
        isAuthenticated: true,
        user: {
          id: '1',
          email: 'test@example.com',
          username: 'testuser',
          role: 'employee',
        },
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <ProtectedRoute requiredRole="employer">
            <TestComponent />
          </ProtectedRoute>
        </TestWrapper>
      );

      expect(screen.queryByTestId('test-component')).not.toBeInTheDocument();
    });

    it('加载状态应该显示加载指示器', () => {
      const store = createTestStore({
        loading: true,
      });

      render(
        <TestWrapper store={store}>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </TestWrapper>
      );

      expect(screen.getByRole('status')).toBeInTheDocument();
    });
  });

  describe('PublicRoute', () => {
    it('未认证用户应该能够访问公共页面', () => {
      const store = createTestStore({
        isAuthenticated: false,
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <PublicRoute>
            <LoginComponent />
          </PublicRoute>
        </TestWrapper>
      );

      expect(screen.getByTestId('login-component')).toBeInTheDocument();
    });

    it('已认证的员工用户应该重定向到票据页面', () => {
      const store = createTestStore({
        isAuthenticated: true,
        user: {
          id: '1',
          email: 'test@example.com',
          username: 'testuser',
          role: 'employee',
        },
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <PublicRoute>
            <LoginComponent />
          </PublicRoute>
        </TestWrapper>
      );

      expect(screen.queryByTestId('login-component')).not.toBeInTheDocument();
    });

    it('已认证的雇主用户应该重定向到员工页面', () => {
      const store = createTestStore({
        isAuthenticated: true,
        user: {
          id: '1',
          email: 'test@example.com',
          username: 'testuser',
          role: 'employer',
        },
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <PublicRoute>
            <LoginComponent />
          </PublicRoute>
        </TestWrapper>
      );

      expect(screen.queryByTestId('login-component')).not.toBeInTheDocument();
    });

    it('被暂停的用户应该能够访问登录页面', () => {
      const store = createTestStore({
        isAuthenticated: true,
        user: {
          id: '1',
          email: 'test@example.com',
          username: 'testuser',
          role: 'employee',
          is_suspended: true,
        },
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <PublicRoute>
            <LoginComponent />
          </PublicRoute>
        </TestWrapper>
      );

      expect(screen.getByTestId('login-component')).toBeInTheDocument();
    });
  });

  describe('PermissionGuard', () => {
    it('未认证用户应该重定向到登录页', () => {
      const store = createTestStore({
        isAuthenticated: false,
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <PermissionGuard requiredRole="employer">
            <TestComponent />
          </PermissionGuard>
        </TestWrapper>
      );

      expect(screen.queryByTestId('test-component')).not.toBeInTheDocument();
    });

    it('员工用户访问需要雇主权限的页面应该重定向', () => {
      const store = createTestStore({
        isAuthenticated: true,
        user: {
          id: '1',
          email: 'test@example.com',
          username: 'testuser',
          role: 'employee',
        },
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <PermissionGuard requiredRole="employer" requiredPermissions={['manage_employees']}>
            <TestComponent />
          </PermissionGuard>
        </TestWrapper>
      );

      expect(screen.queryByTestId('test-component')).not.toBeInTheDocument();
    });

    it('雇主用户应该能够访问需要雇主权限的页面', () => {
      const store = createTestStore({
        isAuthenticated: true,
        user: {
          id: '1',
          email: 'test@example.com',
          username: 'testuser',
          role: 'employer',
        },
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <PermissionGuard requiredRole="employer" requiredPermissions={['manage_employees']}>
            <TestComponent />
          </PermissionGuard>
        </TestWrapper>
      );

      expect(screen.getByTestId('test-component')).toBeInTheDocument();
    });

    it('被暂停的用户应该重定向到登录页', () => {
      const store = createTestStore({
        isAuthenticated: true,
        user: {
          id: '1',
          email: 'test@example.com',
          username: 'testuser',
          role: 'employer',
          is_suspended: true,
        },
        loading: false,
      });

      render(
        <TestWrapper store={store}>
          <PermissionGuard requiredRole="employer">
            <TestComponent />
          </PermissionGuard>
        </TestWrapper>
      );

      expect(screen.queryByTestId('test-component')).not.toBeInTheDocument();
    });
  });
});
