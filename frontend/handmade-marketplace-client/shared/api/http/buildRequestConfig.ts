import { AxiosRequestConfig } from "axios"
import { RequestOptions } from "./type/interface"

function buildRequestConfig({method, url, body, params, config, headers, accessToken}: RequestOptions): AxiosRequestConfig {
  const finalHeaders = {
    ...headers,
    ...(accessToken && !headers.Authorization
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