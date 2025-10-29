import { useEffect } from 'react'
import { useAppSelector, useAppDispatch } from '../store/hooks'
import { 
  fetchEmployees, 
  suspendEmployeeAction, 
  activateEmployeeAction,
  clearError 
} from '../store/slices/employeesSlice'

function EmployeeListPage() {
  const dispatch = useAppDispatch()
  const { employees, loading, error, updating } = useAppSelector(state => state.employees)

  useEffect(() => {
    dispatch(fetchEmployees())
    return () => {
      dispatch(clearError())
    }
  }, [dispatch])

  const handleAction = (id: string, action: 'suspend' | 'activate') => {
    if (action === 'suspend') {
      dispatch(suspendEmployeeAction(id))
    } else {
      dispatch(activateEmployeeAction(id))
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">员工列表</h1>
      {error && <div className="text-red-600">{error}</div>}
      
      {loading ? (
        <div className="text-center py-4">加载中...</div>
      ) : (
        <table className="min-w-full bg-white rounded shadow">
          <thead>
            <tr className="text-left">
              <th className="p-2">邮箱</th>
              <th className="p-2">用户名</th>
              <th className="p-2">角色</th>
              <th className="p-2">状态</th>
              <th className="p-2">操作</th>
            </tr>
          </thead>
          <tbody>
            {employees.map(employee => (
              <tr key={employee.id} className="border-t">
                <td className="p-2">{employee.email}</td>
                <td className="p-2">{employee.username}</td>
                <td className="p-2">
                  <span className={`px-2 py-1 rounded text-xs ${
                    employee.role === 'employer' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                  }`}>
                    {employee.role === 'employer' ? '雇主' : '员工'}
                  </span>
                </td>
                <td className="p-2">
                  <span className={`px-2 py-1 rounded text-xs ${
                    employee.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {employee.is_active ? '正常' : '已停用'}
                  </span>
                </td>
                <td className="p-2 space-x-2">
                  {employee.is_active ? (
                    <button 
                      className="text-red-600 disabled:opacity-50" 
                      onClick={() => handleAction(employee.id, 'suspend')}
                      disabled={updating}
                    >
                      停用
                    </button>
                  ) : (
                    <button 
                      className="text-green-600 disabled:opacity-50" 
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
      )}
    </div>
  )
}

export default EmployeeListPage


