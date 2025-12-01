import { useAuthStore } from "@/entities/auth/model/Store/auth-store";
import axios from "axios";
import { ApiEndpoints } from "./enums";
import { refreshAccessToken } from "./http-request";

export const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

export const axiosInstanceRequest = axiosInstance.interceptors.request.use(config => {
  const token = useAuthStore.getState().accessToken;

  if(token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export const axiosInstanceResponse = axiosInstance.interceptors.response.use((response) => response, async(error) => {
  const originalRequest = error.config;

  if(axios.isAxiosError(error) && error.response?.status === 401 && originalRequest.url !== ApiEndpoints.REFRESH_TOKEN) {
    if(!originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const newAccessToken = await refreshAccessToken();

        if(newAccessToken) {
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

          return axiosInstance(originalRequest)
        }
      } catch (refreshError) {
        return Promise.reject(error);
      }
    }
  }

  return Promise.reject(error);
})