import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { getTickets, createTicket, approveTicket, denyTicket, deleteTicket } from '../../services/tickets'

export interface Ticket {
  id: string
  spent_at: string
  amount: number
  currency: string
  description?: string
  link?: string
  status: 'pending' | 'approved' | 'denied'
  created_at: string
  updated_at: string
  employee_id: string
  employee?: {
    id: string
    username: string
    email: string
  }
}

export interface CreateTicketData {
  spent_at: string
  amount: number
  currency: string
  description?: string
  link?: string
}

export interface TicketsState {
  tickets: Ticket[]
  loading: boolean
  error: string | null
  creating: boolean
  updating: boolean
}

const initialState: TicketsState = {
  tickets: [],
  loading: false,
  error: null,
  creating: false,
  updating: false,
}

// 异步thunk：获取票据列表
export const fetchTickets = createAsyncThunk(
  'tickets/fetchTickets',
  async (_, { rejectWithValue }) => {
    try {
      const response = await getTickets()
      return response
    } catch (error: any) {
      return rejectWithValue(error?.response?.data?.detail || error?.message || '获取票据失败')
    }
  }
)

// 异步thunk：创建票据
export const createNewTicket = createAsyncThunk(
  'tickets/createTicket',
  async (ticketData: CreateTicketData, { rejectWithValue }) => {
    try {
      const response = await createTicket(ticketData)
      return response
    } catch (error: any) {
      return rejectWithValue(error?.response?.data?.detail || error?.message || '创建票据失败')
    }
  }
)

// 异步thunk：批准票据
export const approveTicketAction = createAsyncThunk(
  'tickets/approveTicket',
  async (ticketId: string, { rejectWithValue }) => {
    try {
      const response = await approveTicket(ticketId)
      return { ticketId, response }
    } catch (error: any) {
      return rejectWithValue(error?.response?.data?.detail || error?.message || '批准票据失败')
    }
  }
)

// 异步thunk：拒绝票据
export const denyTicketAction = createAsyncThunk(
  'tickets/denyTicket',
  async (ticketId: string, { rejectWithValue }) => {
    try {
      const response = await denyTicket(ticketId)
      return { ticketId, response }
    } catch (error: any) {
      return rejectWithValue(error?.response?.data?.detail || error?.message || '拒绝票据失败')
    }
  }
)

// 异步thunk：删除票据
export const deleteTicketAction = createAsyncThunk(
  'tickets/deleteTicket',
  async (ticketId: string, { rejectWithValue }) => {
    try {
      await deleteTicket(ticketId)
      return ticketId
    } catch (error: any) {
      return rejectWithValue(error?.response?.data?.detail || error?.message || '删除票据失败')
    }
  }
)

const ticketsSlice = createSlice({
  name: 'tickets',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    clearTickets: (state) => {
      state.tickets = []
    },
  },
  extraReducers: (builder) => {
    builder
      // 获取票据列表
      .addCase(fetchTickets.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchTickets.fulfilled, (state, action) => {
        state.loading = false
        state.tickets = action.payload
        state.error = null
      })
      .addCase(fetchTickets.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      // 创建票据
      .addCase(createNewTicket.pending, (state) => {
        state.creating = true
        state.error = null
      })
      .addCase(createNewTicket.fulfilled, (state, action) => {
        state.creating = false
        state.tickets.unshift(action.payload)
        state.error = null
      })
      .addCase(createNewTicket.rejected, (state, action) => {
        state.creating = false
        state.error = action.payload as string
      })
      // 批准票据
      .addCase(approveTicketAction.pending, (state) => {
        state.updating = true
        state.error = null
      })
      .addCase(approveTicketAction.fulfilled, (state, action) => {
        state.updating = false
        const ticket = state.tickets.find(t => t.id === action.payload.ticketId)
        if (ticket) {
          ticket.status = 'approved'
        }
        state.error = null
      })
      .addCase(approveTicketAction.rejected, (state, action) => {
        state.updating = false
        state.error = action.payload as string
      })
      // 拒绝票据
      .addCase(denyTicketAction.pending, (state) => {
        state.updating = true
        state.error = null
      })
      .addCase(denyTicketAction.fulfilled, (state, action) => {
        state.updating = false
        const ticket = state.tickets.find(t => t.id === action.payload.ticketId)
        if (ticket) {
          ticket.status = 'denied'
        }
        state.error = null
      })
      .addCase(denyTicketAction.rejected, (state, action) => {
        state.updating = false
        state.error = action.payload as string
      })
      // 删除票据
      .addCase(deleteTicketAction.pending, (state) => {
        state.updating = true
        state.error = null
      })
      .addCase(deleteTicketAction.fulfilled, (state, action) => {
        state.updating = false
        state.tickets = state.tickets.filter(t => t.id !== action.payload)
        state.error = null
      })
      .addCase(deleteTicketAction.rejected, (state, action) => {
        state.updating = false
        state.error = action.payload as string
      })
  },
})

export const { clearError, clearTickets } = ticketsSlice.actions
export default ticketsSlice.reducer
