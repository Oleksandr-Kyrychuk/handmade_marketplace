import axios, { AxiosResponse } from "axios";
import { axiosInstance } from "./axiosInstance";
import buildRequestConfig from "./buildRequestConfig";

import { ApiEndpoints } from "./enums";
import { normalizeApiError } from "./normalizeApiError";
import { RequestOptions } from "./types/interfaces";
import { useAuthStore } from "@/entities/auth/model/Store/auth-store";


export async function refreshAccessToken() {
  const authStore = useAuthStore.getState();
  try {
    const response = await axiosInstance.post(ApiEndpoints.REFRESH_TOKEN)

    const newAccessToken = response.data.access;
    
    authStore.setTokens(newAccessToken)

    console.log('refreshAccessToken access_token', newAccessToken)

    return newAccessToken;
  } catch (error) {
    console.error("Error refreshing access token:", error);

    authStore.clearTokens();
    return null;
  }
}

export async function  Request<T>(options:RequestOptions): Promise<T> {
  try {
    const requestConfig = buildRequestConfig(options);
    const response: AxiosResponse<T> = await axiosInstance(requestConfig);

    // console.log('response', response)

    return response.data
  } catch (error: unknown) {
    console.error("API error:", error);


    const normalized = normalizeApiError(error);

    console.error("API error:", normalized);
    throw normalized;
  }
}