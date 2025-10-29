import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { initializeAuth } from '../store/slices/authSlice';
import type { AppDispatch } from '../store';

interface AuthInitializerProps {
  children: React.ReactNode;
}

export function AuthInitializer({ children }: AuthInitializerProps) {
  const dispatch = useDispatch<AppDispatch>();

  useEffect(() => {
    // 初始化认证状态
    dispatch(initializeAuth());
  }, [dispatch]);

  return <>{children}</>;
}
