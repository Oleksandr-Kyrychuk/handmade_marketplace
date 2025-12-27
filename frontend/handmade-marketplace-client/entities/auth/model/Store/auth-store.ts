import { create } from "zustand";

interface IAuthState {
  accessToken: string | null;
  setTokens: (access: string) => void;
  clearTokens: () => void;
}

export const useAuthStore = create<IAuthState>(set => ({
  accessToken: null,

  setTokens:(accessToken) => set({
    accessToken: accessToken
  }),

  clearTokens:() => set({
    accessToken: null
  })
}))