import { Navigate } from 'react-router-dom';

interface PublicRouteProps {
  children: React.ReactNode;
}

function PublicRoute({ children }: PublicRouteProps) {
  const token = localStorage.getItem('token');

  // 如果已经登录，重定向到票据页面
  if (token) {
    return <Navigate to='/tickets' replace />;
  }

  return <>{children}</>;
}

export default PublicRoute;
