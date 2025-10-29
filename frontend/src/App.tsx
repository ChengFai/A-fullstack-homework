import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAppSelector, useAppDispatch } from './store/hooks'
import { logoutUser } from './store/slices/authSlice'
import './index.css'

function App() {
  const navigate = useNavigate()
  const dispatch = useAppDispatch()
  const { isAuthenticated, user } = useAppSelector(state => state.auth)
  
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-6xl px-4 py-4 flex justify-between">
          <nav className="space-x-4">
            {isAuthenticated && (
              <>
                <Link to="/tickets" className="text-blue-600">票据</Link>
                {user?.role === 'employer' && (
                  <Link to="/employees" className="text-blue-600">员工</Link>
                )}
              </>
            )}
          </nav>
          <div className="space-x-4">
            {isAuthenticated ? (
              <button
                className="text-red-600"
                onClick={() => {
                  dispatch(logoutUser())
                  navigate('/login')
                }}
              >退出</button>
            ) : (
              <>
                <Link to="/login" className="text-blue-600">登录</Link>
                <Link to="/register" className="text-green-600">注册</Link>
              </>
            )}
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl p-4">
        <Outlet />
      </main>
    </div>
  )
}

export default App


