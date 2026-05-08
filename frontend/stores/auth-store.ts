import { create } from "zustand";

interface User {
  id: string;
  username: string;
  email: string;
  role: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== "undefined" ? localStorage.getItem("auth_token") : null,
  user: null,
  isAuthenticated: !!(typeof window !== "undefined" ? localStorage.getItem("auth_token") : false),
  
  setToken: (token: string) => {
    localStorage.setItem("auth_token", token);
    set({ token, isAuthenticated: true });
  },
  
  setUser: (user: User) => set({ user }),
  
  logout: () => {
    localStorage.removeItem("auth_token");
    set({ token: null, user: null, isAuthenticated: false });
  },
}));
