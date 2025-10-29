import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import {
  getEmployees,
  suspendEmployee,
  activateEmployee,
} from '../../services/employees';

export interface Employee {
  id: string;
  username: string;
  email: string;
  role: 'employee' | 'employer';
  is_suspended: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmployeesState {
  employees: Employee[];
  loading: boolean;
  error: string | null;
  updating: boolean;
}

const initialState: EmployeesState = {
  employees: [],
  loading: false,
  error: null,
  updating: false,
};

// 异步thunk：获取员工列表
export const fetchEmployees = createAsyncThunk(
  'employees/fetchEmployees',
  async (_, { rejectWithValue }) => {
    try {
      const response = await getEmployees();
      return response;
    } catch (error: any) {
      return rejectWithValue(
        error?.response?.data?.detail || error?.message || '获取员工列表失败'
      );
    }
  }
);

// 异步thunk：暂停员工
export const suspendEmployeeAction = createAsyncThunk(
  'employees/suspendEmployee',
  async (employeeId: string, { rejectWithValue }) => {
    try {
      const response = await suspendEmployee(employeeId);
      return { employeeId, response };
    } catch (error: any) {
      return rejectWithValue(
        error?.response?.data?.detail || error?.message || '暂停员工失败'
      );
    }
  }
);

// 异步thunk：激活员工
export const activateEmployeeAction = createAsyncThunk(
  'employees/activateEmployee',
  async (employeeId: string, { rejectWithValue }) => {
    try {
      const response = await activateEmployee(employeeId);
      return { employeeId, response };
    } catch (error: any) {
      return rejectWithValue(
        error?.response?.data?.detail || error?.message || '激活员工失败'
      );
    }
  }
);

const employeesSlice = createSlice({
  name: 'employees',
  initialState,
  reducers: {
    clearError: state => {
      state.error = null;
    },
    clearEmployees: state => {
      state.employees = [];
    },
  },
  extraReducers: builder => {
    builder
      // 获取员工列表
      .addCase(fetchEmployees.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEmployees.fulfilled, (state, action) => {
        state.loading = false;
        state.employees = action.payload;
        state.error = null;
      })
      .addCase(fetchEmployees.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 暂停员工
      .addCase(suspendEmployeeAction.pending, state => {
        state.updating = true;
        state.error = null;
      })
      .addCase(suspendEmployeeAction.fulfilled, (state, action) => {
        state.updating = false;
        const employee = state.employees.find(
          e => e.id === action.payload.employeeId
        );
        if (employee) {
          employee.is_suspended = true;
        }
        state.error = null;
      })
      .addCase(suspendEmployeeAction.rejected, (state, action) => {
        state.updating = false;
        state.error = action.payload as string;
      })
      // 激活员工
      .addCase(activateEmployeeAction.pending, state => {
        state.updating = true;
        state.error = null;
      })
      .addCase(activateEmployeeAction.fulfilled, (state, action) => {
        state.updating = false;
        const employee = state.employees.find(
          e => e.id === action.payload.employeeId
        );
        if (employee) {
          employee.is_suspended = false;
        }
        state.error = null;
      })
      .addCase(activateEmployeeAction.rejected, (state, action) => {
        state.updating = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, clearEmployees } = employeesSlice.actions;
export default employeesSlice.reducer;
