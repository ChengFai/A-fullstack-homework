import { Navigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';
import { PageLoading } from './LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'employee' | 'employer';
  fallbackPath?: string;
}

function ProtectedRoute({ children, requiredRole, fallbackPath = '/tickets' }: ProtectedRouteProps) {
  const location = useLocation();
  const { isAuthenticated, user, loading } = useAppSelector(state => state.auth);

  // 如果正在加载认证状态，显示加载状态
  if (loading) {
    return <PageLoading text="验证身份中..." />;
  }

  // 如果没有认证，重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to='/login' state={{ from: location }} replace />;
  }

  // 如果用户被暂停，重定向到登录页并清除认证状态
  if (user?.is_suspended) {
    return <Navigate to='/login' state={{ message: '您的账户已被暂停' }} replace />;
  }

  // 如果指定了角色要求，检查用户角色
  if (requiredRole && user?.role !== requiredRole) {
    // 根据用户角色重定向到合适的页面
    const redirectPath = user?.role === 'employee' ? '/tickets' : '/employees';
    return <Navigate to={redirectPath} replace />;
  }

  return <>{children}</>;
}

export default ProtectedRoute;
