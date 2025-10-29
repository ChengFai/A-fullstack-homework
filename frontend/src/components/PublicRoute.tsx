import { Navigate } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';

interface PublicRouteProps {
  children: React.ReactNode;
}

function PublicRoute({ children }: PublicRouteProps) {
  const { isAuthenticated, user, loading } = useAppSelector(state => state.auth);

  // 如果正在加载认证状态，显示加载状态
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // 如果已经登录，根据用户角色重定向到合适的页面
  if (isAuthenticated && user) {
    // 如果用户被暂停，允许访问登录页面（用于显示暂停消息）
    if (user.is_suspended) {
      return <>{children}</>;
    }
    
    // 根据用户角色重定向
    const redirectPath = user.role === 'employee' ? '/tickets' : '/employees';
    return <Navigate to={redirectPath} replace />;
  }

  return <>{children}</>;
}

export default PublicRoute;
