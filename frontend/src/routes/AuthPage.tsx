import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { 
  loginUser, 
  registerUser, 
  checkUserExists, 
  clearError, 
  clearUserExists 
} from '../store/slices/authSlice';

function AuthPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const { 
    loading, 
    error, 
    isAuthenticated, 
    checkingUser 
  } = useAppSelector(state => state.auth);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [username, setUsername] = useState('');
  const [role, setRole] = useState<'employee' | 'employer' | ''>('');
  const [localError, setLocalError] = useState('');

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
      dispatch(clearUserExists());
    };
  }, [dispatch]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');
    dispatch(clearError());

    // 先检查用户是否存在
    try {
      const checkResult = await dispatch(checkUserExists(email));
      const userExists = checkResult.payload as boolean;
      
      if (userExists) {
        // 用户存在，执行登录
        dispatch(loginUser({ email, password }));
      } else {
        // 用户不存在，执行注册
        // 注册模式验证
        if (password !== confirmPassword) {
          setLocalError('两次输入的密码不一致');
          return;
        }
        if (!role) {
          setLocalError('请选择角色');
          return;
        }
        if (!username.trim()) {
          setLocalError('请输入用户名');
          return;
        }
        
        dispatch(registerUser({ email, password, username, role }));
      }
    } catch (error) {
      setLocalError('检查用户状态失败，请重试');
    }
  };

  const getButtonText = () => {
    if (loading) {
      return '处理中...';
    }
    if (checkingUser) {
      return '检查中...';
    }
    return '提交';
  };

  const getTitle = () => {
    if (checkingUser) {
      return '检查用户';
    }
    return '登录/注册';
  };

  return (
    <div className='mt-10 flex items-center justify-center bg-gray-50'>
      <div className='max-w-md w-full bg-white p-8 rounded-lg shadow-md'>
        <h1 className='text-2xl font-bold text-center mb-6'>{getTitle()}</h1>

        {(error || localError) && (
          <div className='mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded'>
            {error || localError}
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
              htmlFor='username'
              className='block text-sm font-medium text-gray-700 mb-1'
            >
              用户名
            </label>
            <input
              id='username'
              type='text'
              className='w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
              placeholder='请输入用户名'
              value={username}
              onChange={e => setUsername(e.target.value)}
            />
          </div>

          <div>
            <label
              htmlFor='role'
              className='block text-sm font-medium text-gray-700 mb-1'
            >
              角色
            </label>
            <select
              id='role'
              className='w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
              value={role}
              onChange={e => setRole(e.target.value as 'employee' | 'employer')}
            >
              <option value=''>请选择角色</option>
              <option value='employee'>员工</option>
              <option value='employer'>雇主</option>
            </select>
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
              minLength={6}
              className='w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
              placeholder='请输入密码（至少6位）'
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>

          <div>
            <label
              htmlFor='confirmPassword'
              className='block text-sm font-medium text-gray-700 mb-1'
            >
              确认密码
            </label>
            <input
              id='confirmPassword'
              type='password'
              className='w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
              placeholder='请再次输入密码'
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
            />
          </div>

          <button
            type='submit'
            disabled={loading || checkingUser}
            className='w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed'
          >
            {getButtonText()}
          </button>
        </form>
      </div>
    </div>
  );
}

export default AuthPage;
