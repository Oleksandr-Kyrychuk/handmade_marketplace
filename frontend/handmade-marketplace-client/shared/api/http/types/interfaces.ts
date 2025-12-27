import { AxiosRequestConfig } from "axios";
import { ApiEndpoints, HttpMethods } from "../enums";

export type RequestOptions = {
  readonly method: HttpMethods;
  readonly url: ApiEndpoints;
  readonly accessToken?: string,
  readonly body?: unknown;
  readonly params?: Record<string, string | number>;
  readonly config?: AxiosRequestConfig,
  readonly skipAuth?: boolean;
  readonly headers?: Record<string, string>
}

export type ApiError = {
  message: string,
  statusCode?: number;
  original?: unknown;
  fieldErrors?: Record<string, string>;
}

export type ApiResult = {
  readonly url: string,
  readonly ok: boolean
  readonly status: number,
  readonly statusText: string,
  readonly body: any,
  readonly dataErrors?: Record<string, string[]>
}
