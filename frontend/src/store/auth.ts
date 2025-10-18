import { create } from 'zustand';
import api from '../api/client';

const STORAGE_KEY = 'mouqarr-auth';

interface User {
  id: number;
  name: string;
  role: string;
  email?: string;
}

interface AuthState {
  token?: string;
  user?: User;
  login: (identifier: string) => Promise<void>;
}

const storedValue = typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null;
const initial = storedValue ? (JSON.parse(storedValue) as { token: string; user: User }) : undefined;

export const useAuthStore = create<AuthState>((set) => ({
  token: initial?.token,
  user: initial?.user,
  login: async (identifier: string) => {
    const response = await api.post<{ access_token: string; user: User }>('/auth/login', { identifier });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(response));
    set({ token: response.access_token, user: response.user });
  }
}));
