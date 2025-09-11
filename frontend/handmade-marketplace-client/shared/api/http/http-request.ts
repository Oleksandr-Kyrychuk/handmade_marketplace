import axios, { AxiosResponse } from "axios";
import { axiosInstance } from "./axiosInstance";
import buildRequestConfig from "./buildRequestConfig";

import { ApiEndpoints } from "./enums";
import { normalizeApiError } from "./normalizeApiError";

// import { RequestOptions } from "./type/interface";
// import { getQueryClient } from "../helpers/getQueryClient";
// import { normalizeApiError } from "./normalizeApiError";


export async function refreshAccessToken() {
  try {
    const response = await axiosInstance.post(ApiEndpoints.REFRESHTOKEN)

    const access_token = response.data.access;
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

    console.log('refreshAccessToken access_token', access_token)

    return access_token;
  } catch (error) {
    console.error("Error refreshing access token:", error);


    // const queryClient = getQueryClient();
    // queryClient.removeQueries({ queryKey: ['user']})

    return null;
  }
}

export async function  Request<T>(options:RequestOptions): Promise<T> {
  const { method, url, body, params, config, headers, accessToken } = options;

  try {
    const requestConfig = buildRequestConfig({ method, url, body, params, config, headers, accessToken });
    const response: AxiosResponse<T> = await axiosInstance(requestConfig);

    // console.log('response', response)

    return response.data
  } catch (error: unknown) {
    console.error("API error:", error);
    // if(axios.isAxiosError(error) && error.response?.status === 401) {
    //   const { isAuthInitialized } = store.getState().token;

    //   console.log('error isAuthInitialized', isAuthInitialized)
    //   if(!isAuthInitialized) {
    //     return Promise.reject(error)
    //   }

    //   const newAccessToken = await refreshAccessToken();
      
    //   if(newAccessToken) {
    //     const retryConfig = buildRequestConfig({ method, url, body, params, config, headers, accessToken });
    //     const retryResponse = await axiosInstance(retryConfig);

    //     return retryResponse.data
    //   } else {
    //     store.dispatch(clearToken());
    //      store.dispatch(setAuthInitialized(false));

    //     getQueryClient().removeQueries({ queryKey: ["user"]})

    //     return Promise.reject(new Error('Unauthorized'))
    //   }
    // }

    // const normalized = normalizeApiError(error);

    // console.error("API error:", normalized);
    // throw normalized;
  }
}