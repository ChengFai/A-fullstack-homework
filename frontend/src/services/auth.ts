import { api } from './http'

type LoginReq = { email: string; password: string }
type RegisterReq = { email: string; password: string; role: 'employee' | 'employer'; username: string }
type AuthRes = { token: string; user: { id: string; email: string; username: string; role: 'employee' | 'employer' } }

export async function login(body: LoginReq): Promise<AuthRes> {
  const { data } = await api.post('/auth/login', body)
  return data
}

export async function register(body: RegisterReq): Promise<AuthRes> {
  const { data } = await api.post('/auth/register', body)
  return data
}


