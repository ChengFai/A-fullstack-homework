import { useEffect } from 'react';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import {
  fetchEmployees,
  suspendEmployeeAction,
  activateEmployeeAction,
  clearError,
} from '../store/slices/employeesSlice';

function EmployeeListPage() {
  const dispatch = useAppDispatch();
  const { employees, loading, error, updating } = useAppSelector(
    state => state.employees
  );

  useEffect(() => {
    dispatch(fetchEmployees());
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  const handleAction = (id: string, action: 'suspend' | 'activate') => {
    if (action === 'suspend') {
      dispatch(suspendEmployeeAction(id));
    } else {
      dispatch(activateEmployeeAction(id));
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">员工管理</h1>
            <p className="text-gray-600 mt-1">管理系统中的所有员工账户</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full"></div>
            <span className="text-sm text-gray-500">系统正常</span>
          </div>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}

      {/* 员工列表 */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">员工列表</h2>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                共 {employees.length} 名员工
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-xs text-gray-500">
                  {employees.filter(emp => !emp.is_suspended).length} 活跃
                </span>
                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                <span className="text-xs text-gray-500">
                  {employees.filter(emp => emp.is_suspended).length} 停用
                </span>
              </div>
            </div>
          </div>
        </div>
        
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="flex items-center space-x-2">
              <svg className="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-gray-600">加载中...</span>
            </div>
          </div>
        ) : employees.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-6">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">暂无员工数据</h3>
            <p className="text-gray-500 text-center max-w-sm">
              系统中暂无员工数据，请先注册员工账户后再进行管理操作。
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户信息</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {employees.map(employee => (
                  <tr key={employee.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                          <span className="text-gray-600 font-medium">
                            {employee.username.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {employee.username}
                          </div>
                          <div className="text-sm text-gray-500">
                            {employee.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          employee.role === 'employer'
                            ? 'bg-purple-100 text-purple-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {employee.role === 'employer' ? '雇主' : '员工'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          !employee.is_suspended
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {!employee.is_suspended ? '正常' : '已停用'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {!employee.is_suspended ? (
                        <button
                          className="text-red-600 hover:text-red-900 disabled:opacity-50 disabled:cursor-not-allowed bg-red-50 hover:bg-red-100 px-3 py-1 rounded-md transition-colors duration-200"
                          onClick={() => handleAction(employee.id, 'suspend')}
                          disabled={updating}
                        >
                          停用
                        </button>
                      ) : (
                        <button
                          className="text-green-600 hover:text-green-900 disabled:opacity-50 disabled:cursor-not-allowed bg-green-50 hover:bg-green-100 px-3 py-1 rounded-md transition-colors duration-200"
                          onClick={() => handleAction(employee.id, 'activate')}
                          disabled={updating}
                        >
                          恢复
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default EmployeeListPage;
