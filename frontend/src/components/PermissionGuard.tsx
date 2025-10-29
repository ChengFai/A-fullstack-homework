import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';

interface PermissionGuardProps {
  children: ReactNode;
  requiredRole?: 'employee' | 'employer';
  requiredPermissions?: string[];
  fallbackPath?: string;
}

/**
 * 权限守卫组件 - 用于保护需要特定权限的页面或组件
 * 确保只有具有相应权限的用户才能访问受保护的内容
 */
function PermissionGuard({ 
  children, 
  requiredRole, 
  requiredPermissions = [], 
  fallbackPath 
}: PermissionGuardProps) {
  const { user, isAuthenticated } = useAppSelector(state => state.auth);

  // 如果未认证，重定向到登录页
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  // 如果用户被暂停，重定向到登录页
  if (user.is_suspended) {
    return <Navigate to="/login" state={{ message: '您的账户已被暂停' }} replace />;
  }

  // 检查角色权限
  if (requiredRole && user.role !== requiredRole) {
    const redirectPath = fallbackPath || (user.role === 'employee' ? '/tickets' : '/employees');
    return <Navigate to={redirectPath} replace />;
  }

  // 检查特定权限（如果需要的话）
  if (requiredPermissions.length > 0) {
    // 这里可以根据需要扩展权限检查逻辑
    // 例如检查用户是否有特定的权限标记
    const hasRequiredPermissions = requiredPermissions.every(permission => {
      // 根据角色判断权限
      switch (permission) {
        case 'view_all_tickets':
          return user.role === 'employer';
        case 'manage_employees':
          return user.role === 'employer';
        case 'create_tickets':
          return user.role === 'employee' || user.role === 'employer';
        case 'view_own_tickets':
          return user.role === 'employee' || user.role === 'employer';
        default:
          return false;
      }
    });

    if (!hasRequiredPermissions) {
      const redirectPath = fallbackPath || (user.role === 'employee' ? '/tickets' : '/employees');
      return <Navigate to={redirectPath} replace />;
    }
  }

  return <>{children}</>;
}

export default PermissionGuard;
