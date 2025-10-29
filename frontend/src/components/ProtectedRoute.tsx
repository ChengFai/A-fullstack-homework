import { Navigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'employee' | 'employer';
}

function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const location = useLocation();
  const { isAuthenticated, user } = useAppSelector(state => state.auth);

  // 如果没有认证，重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to='/login' state={{ from: location }} replace />;
  }

  // 如果指定了角色要求，检查用户角色
  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to='/tickets' replace />;
  }

  return <>{children}</>;
}

export default ProtectedRoute;
