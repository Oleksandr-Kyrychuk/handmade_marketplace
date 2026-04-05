import { isAxiosError } from "axios";
import { ApiError } from "./types/interfaces";


export function normalizeApiError(error: unknown): ApiError {
  if (isAxiosError(error)) {
    const row = error.response?.data;

    const message =
      typeof row === 'string'
        ? row.startsWith('<!DOCTYPE html')
          ? 'Server error'
          : row
        : row?.message ?? row?.error?.message ?? 'Server error';

    const possibleFieldErrors =
      row && typeof row === 'object'
        ? row?.data || row?.errors || row?.error?.errors
        : undefined;

    let fieldErrors: Record<string, string> | undefined;

    if (Array.isArray(possibleFieldErrors)) {
      fieldErrors = Object.fromEntries(
        possibleFieldErrors
          .filter((e) => e.field && e.message)
          .map((e) => [e.field, e.message])
      );
    }

    else if (possibleFieldErrors && typeof possibleFieldErrors === 'object') {
      fieldErrors = Object.fromEntries(
        Object.entries(possibleFieldErrors)
          .filter(([_, v]) => Array.isArray(v) && typeof v[0] === 'string')
          .map(([key, value]) => [key, (value as string[])[0]])
      );
    }

    return {
      message,
      statusCode: error.response?.status,
      original: row,
      fieldErrors,
    };
  }

  if (error instanceof Error) {
    return { message: error.message, original: error };
  }

  return { message: 'Unknown Error', original: error };
}