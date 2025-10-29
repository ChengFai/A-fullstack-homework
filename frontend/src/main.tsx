import React from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import App from './App';
import './index.css';
import AuthPage from './routes/AuthPage';
import TicketListPage from './routes/TicketListPage';
import EmployeeListPage from './routes/EmployeeListPage';
import ProtectedRoute from './components/ProtectedRoute';
import PublicRoute from './components/PublicRoute';
import PermissionGuard from './components/PermissionGuard';
import { AuthInitializer } from './components/AuthInitializer';
import ErrorBoundary from './components/ErrorBoundary';
import GlobalErrorHandler from './components/GlobalErrorHandler';
import { NetworkStatusIndicator } from './components/LoadingSpinner';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        path: '/',
        element: (
          <PublicRoute>
            <AuthPage />
          </PublicRoute>
        ),
      },
      {
        path: '/auth',
        element: (
          <PublicRoute>
            <AuthPage />
          </PublicRoute>
        ),
      },
      {
        path: '/tickets',
        element: (
          <ProtectedRoute>
            <TicketListPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/employees',
        element: (
          <ProtectedRoute>
            <PermissionGuard requiredRole="employer" requiredPermissions={['manage_employees']}>
              <EmployeeListPage />
            </PermissionGuard>
          </ProtectedRoute>
        ),
      },
    ],
  },
]);

createRoot(document.getElementById('root')!).render(
  <Provider store={store}>
    <ErrorBoundary>
      <AuthInitializer>
        <NetworkStatusIndicator />
        <GlobalErrorHandler />
        <RouterProvider router={router} />
      </AuthInitializer>
    </ErrorBoundary>
  </Provider>
);
