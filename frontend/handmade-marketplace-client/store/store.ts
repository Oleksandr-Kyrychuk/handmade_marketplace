import { create } from "zustand";

const useStore = create((set) => ({
  token: '',
  setAuthInitialized: false,

  setToken: (token) => set((state) => ({token: token, setAuthInitialized: true})),
  clearToken: () => set((state) => ({token: '', setAuthInitialized: false}))
}))

export default useStore;