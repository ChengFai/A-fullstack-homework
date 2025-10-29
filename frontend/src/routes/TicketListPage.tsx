import { useEffect, useState } from 'react'
import { useAppSelector, useAppDispatch } from '../store/hooks'
import { 
  fetchTickets, 
  createNewTicket, 
  approveTicketAction, 
  denyTicketAction, 
  deleteTicketAction,
  clearError 
} from '../store/slices/ticketsSlice'

function TicketListPage() {
  const dispatch = useAppDispatch()
  const { tickets, loading, error, creating, updating } = useAppSelector(state => state.tickets)
  const { user } = useAppSelector(state => state.auth)
  
  const [form, setForm] = useState({ 
    spent_at: '', 
    amount: 0, 
    currency: 'USD', 
    description: '', 
    link: '' 
  })

  useEffect(() => {
    dispatch(fetchTickets())
    return () => {
      dispatch(clearError())
    }
  }, [dispatch])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    dispatch(createNewTicket({ 
      ...form, 
      amount: Number(form.amount) 
    }))
    setForm({ spent_at: '', amount: 0, currency: 'USD', description: '', link: '' })
  }

  const handleAction = (id: string, type: 'approve' | 'deny' | 'delete') => {
    if (type === 'approve') {
      dispatch(approveTicketAction(id))
    } else if (type === 'deny') {
      dispatch(denyTicketAction(id))
    } else {
      dispatch(deleteTicketAction(id))
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">票据列表</h1>
      {error && <div className="text-red-600">{error}</div>}
      
      {user?.role === 'employee' && (
        <form onSubmit={submit} className="bg-white p-4 rounded shadow grid grid-cols-2 gap-2">
          <input 
            className="border p-2" 
            type="datetime-local" 
            value={form.spent_at} 
            onChange={e => setForm({ ...form, spent_at: e.target.value })} 
            required
          />
          <input 
            className="border p-2" 
            type="number" 
            step="0.01" 
            value={form.amount} 
            onChange={e => setForm({ ...form, amount: Number(e.target.value) })} 
            required
          />
          <input 
            className="border p-2" 
            value={form.currency} 
            onChange={e => setForm({ ...form, currency: e.target.value })} 
            required
          />
          <input 
            className="border p-2" 
            placeholder="描述" 
            value={form.description} 
            onChange={e => setForm({ ...form, description: e.target.value })} 
          />
          <input 
            className="border p-2" 
            placeholder="链接" 
            value={form.link} 
            onChange={e => setForm({ ...form, link: e.target.value })} 
          />
          <button 
            className="bg-blue-600 text-white p-2 rounded disabled:opacity-50" 
            type="submit"
            disabled={creating}
          >
            {creating ? '创建中...' : '新增'}
          </button>
        </form>
      )}
      
      {loading ? (
        <div className="text-center py-4">加载中...</div>
      ) : (
        <table className="min-w-full bg-white rounded shadow">
          <thead>
            <tr className="text-left">
              <th className="p-2">时间</th>
              <th className="p-2">金额</th>
              <th className="p-2">币种</th>
              <th className="p-2">状态</th>
              <th className="p-2">操作</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map(ticket => (
              <tr key={ticket.id} className="border-t">
                <td className="p-2">{new Date(ticket.spent_at).toLocaleString()}</td>
                <td className="p-2">{ticket.amount}</td>
                <td className="p-2">{ticket.currency}</td>
                <td className="p-2">
                  <span className={`px-2 py-1 rounded text-xs ${
                    ticket.status === 'approved' ? 'bg-green-100 text-green-800' :
                    ticket.status === 'denied' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {ticket.status === 'approved' ? '已批准' : 
                     ticket.status === 'denied' ? '已拒绝' : '待处理'}
                  </span>
                </td>
                <td className="p-2 space-x-2">
                  {user?.role === 'employer' && ticket.status === 'pending' && (
                    <>
                      <button 
                        className="text-green-600 disabled:opacity-50" 
                        onClick={() => handleAction(ticket.id, 'approve')}
                        disabled={updating}
                      >
                        批准
                      </button>
                      <button 
                        className="text-red-600 disabled:opacity-50" 
                        onClick={() => handleAction(ticket.id, 'deny')}
                        disabled={updating}
                      >
                        拒绝
                      </button>
                    </>
                  )}
                  {user?.role === 'employee' && ticket.status === 'pending' && (
                    <button 
                      className="text-red-600 disabled:opacity-50" 
                      onClick={() => handleAction(ticket.id, 'delete')}
                      disabled={updating}
                    >
                      删除
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

export default TicketListPage