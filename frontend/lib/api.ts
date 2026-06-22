import { appConfig } from "@/lib/env";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function requestJson<T>(
  path: string,
  token: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`${appConfig.apiBaseUrl}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    method: init?.method,
    body: init?.body,
    cache: "no-store"
  });

  if (!response.ok) {
    const fallback = `Request failed with status ${response.status}`;
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(payload?.detail ?? fallback, response.status);
  }

  return (await response.json()) as T;
}

export async function fetchJson<T>(path: string, token: string): Promise<T> {
  return requestJson<T>(path, token);
}

export async function patchJson<TResponse, TPayload>(
  path: string,
  token: string,
  payload: TPayload
): Promise<TResponse> {
  return requestJson<TResponse>(path, token, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}
