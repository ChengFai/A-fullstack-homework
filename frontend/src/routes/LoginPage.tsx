import { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { loginUser, clearError } from '../store/slices/authSlice';

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const { loading, error, isAuthenticated } = useAppSelector(
    state => state.auth
  );

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // 获取重定向目标，如果没有则默认为/tickets
  const from = (location.state as any)?.from?.pathname || '/tickets';

  // 如果已经登录，重定向到目标页面
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  // 清除错误信息
  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    dispatch(clearError());
    dispatch(loginUser({ email, password }));
  };

  return (
    <div className='mt-10 flex items-center justify-center bg-gray-50'>
      <div className='max-w-md w-full bg-white p-8 rounded-lg shadow-md'>
        <h1 className='text-2xl font-bold text-center mb-6'>登录</h1>

        {error && (
          <div className='mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded'>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className='space-y-4'>
          <div>
            <label
              htmlFor='email'
              className='block text-sm font-medium text-gray-700 mb-1'
            >
              邮箱
            </label>
            <input
              id='email'
              type='email'
              required
              className='w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
              placeholder='请输入邮箱'
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label
              htmlFor='password'
              className='block text-sm font-medium text-gray-700 mb-1'
            >
              密码
            </label>
            <input
              id='password'
              type='password'
              required
              className='w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
              placeholder='请输入密码'
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>

          <button
            type='submit'
            disabled={loading}
            className='w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed'
          >
            {loading ? '登录中...' : '登录'}
          </button>
        </form>

        <div className='mt-6 text-center'>
          <p className='text-gray-600'>
            还没有账户？{' '}
            <Link
              to='/register'
              className='text-blue-600 hover:text-blue-800 font-medium'
            >
              立即注册
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
