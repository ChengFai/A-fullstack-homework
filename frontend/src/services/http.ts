import axios, { AxiosError, AxiosResponse } from 'axios';
import { store } from '../store';
import { logoutUser } from '../store/slices/authSlice';

// 错误类型定义
export interface ApiError {
  message: string;
  code?: string;
  status?: number;
  timestamp?: string;
}

// 网络错误类型
export enum NetworkErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

// 错误消息映射
const ERROR_MESSAGES: Record<number, string> = {
  400: '请求参数错误',
  401: '未授权访问，请重新登录',
  403: '权限不足，无法访问此资源',
  404: '请求的资源不存在',
  409: '数据冲突，请检查输入',
  422: '数据验证失败',
  429: '请求过于频繁，请稍后再试',
  500: '服务器内部错误',
  502: '网关错误',
  503: '服务暂时不可用',
  504: '网关超时'
};

// 创建axios实例
export const api = axios.create({
  baseURL: (import.meta as any).env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000, // 10秒超时
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers = config.headers || {};
      (config.headers as any)['Authorization'] = `Bearer ${token}`;
    }
    
    // 添加请求时间戳
    config.metadata = { startTime: new Date() };
    
    return config;
  },
  error => {
    return Promise.reject(createApiError(error, NetworkErrorType.NETWORK_ERROR));
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // 计算请求耗时
    const endTime = new Date();
    const startTime = (response.config as any).metadata?.startTime;
    if (startTime) {
      const duration = endTime.getTime() - startTime.getTime();
      console.log(`API请求耗时: ${duration}ms`);
    }
    
    return response;
  },
  (error: AxiosError) => {
    const apiError = createApiError(error);
    
    // 处理不同类型的错误
    switch (error.response?.status) {
      case 401:
        // 未授权，清除token并登出
        localStorage.removeItem('token');
        store.dispatch(logoutUser());
        break;
      case 403:
        // 权限不足，可能需要重新登录
        console.warn('权限不足:', apiError.message);
        break;
      case 429:
        // 请求过于频繁，延迟重试
        console.warn('请求过于频繁，请稍后再试');
        break;
      case 500:
      case 502:
      case 503:
      case 504:
        // 服务器错误，可以尝试重试
        console.error('服务器错误:', apiError.message);
        break;
      default:
        console.error('API错误:', apiError.message);
    }
    
    return Promise.reject(apiError);
  }
);

// 创建标准化的API错误
function createApiError(error: AxiosError, type?: NetworkErrorType): ApiError {
  let message = '未知错误';
  let code = type || NetworkErrorType.UNKNOWN_ERROR;
  
  if (error.response) {
    // 服务器响应了错误状态码
    const status = error.response.status;
    message = ERROR_MESSAGES[status] || `服务器错误 (${status})`;
    code = getErrorCodeFromStatus(status);
    
    // 尝试从响应中获取更详细的错误信息
    const responseData = error.response.data as any;
    if (responseData?.detail) {
      message = responseData.detail;
    } else if (responseData?.message) {
      message = responseData.message;
    } else if (responseData?.error) {
      message = responseData.error;
    }
  } else if (error.request) {
    // 请求已发出但没有收到响应
    if (error.code === 'ECONNABORTED') {
      message = '请求超时，请检查网络连接';
      code = NetworkErrorType.TIMEOUT_ERROR;
    } else {
      message = '网络连接失败，请检查网络设置';
      code = NetworkErrorType.NETWORK_ERROR;
    }
  } else {
    // 其他错误
    message = error.message || '请求配置错误';
  }
  
  return {
    message,
    code,
    status: error.response?.status,
    timestamp: new Date().toISOString()
  };
}

// 根据状态码获取错误类型
function getErrorCodeFromStatus(status: number): NetworkErrorType {
  if (status >= 500) return NetworkErrorType.SERVER_ERROR;
  if (status === 401) return NetworkErrorType.AUTH_ERROR;
  if (status === 422) return NetworkErrorType.VALIDATION_ERROR;
  return NetworkErrorType.UNKNOWN_ERROR;
}

// 重试机制
export const retryRequest = async (
  requestFn: () => Promise<any>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<any> => {
  let lastError: any;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      
      // 如果是网络错误或服务器错误，可以重试
      const apiError = error as ApiError;
      if (apiError.code === NetworkErrorType.NETWORK_ERROR || 
          apiError.code === NetworkErrorType.SERVER_ERROR ||
          apiError.code === NetworkErrorType.TIMEOUT_ERROR) {
        
        if (i < maxRetries - 1) {
          console.log(`请求失败，${delay}ms后重试 (${i + 1}/${maxRetries})`);
          await new Promise(resolve => setTimeout(resolve, delay));
          delay *= 2; // 指数退避
          continue;
        }
      }
      
      // 其他错误或重试次数用完，直接抛出
      break;
    }
  }
  
  throw lastError;
};

// 检查网络连接状态
export const checkNetworkStatus = (): boolean => {
  return navigator.onLine;
};

// 监听网络状态变化
export const onNetworkStatusChange = (callback: (isOnline: boolean) => void) => {
  const handleOnline = () => callback(true);
  const handleOffline = () => callback(false);
  
  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);
  
  return () => {
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
  };
};
