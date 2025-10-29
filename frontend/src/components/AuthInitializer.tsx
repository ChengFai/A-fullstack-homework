import { useEffect } from 'react'
import { useAppDispatch } from '../store/hooks'
import { initializeAuth } from '../store/slices/authSlice'

interface AuthInitializerProps {
  children: React.ReactNode
}

export function AuthInitializer({ children }: AuthInitializerProps) {
  const dispatch = useAppDispatch()

  useEffect(() => {
    // 初始化认证状态
    dispatch(initializeAuth())
  }, [dispatch])

  return <>{children}</>
}
