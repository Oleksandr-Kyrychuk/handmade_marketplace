import { AxiosRequestConfig } from "axios"
import { RequestOptions } from "./types/interfaces";


function buildRequestConfig(options: RequestOptions): AxiosRequestConfig {
  const { method, url, body, params, config, headers, accessToken } = options;
  const finalHeaders = {
    ...headers,
    ...(accessToken && !headers?.['Authorization']
      ? { Authorization: `Bearer ${accessToken}` }
      : {}),
  };

  return {
    method,
    url,
    data: body,
    params,
    withCredentials: true,
    headers: finalHeaders,
    ...config
  };
}

export default buildRequestConfig;