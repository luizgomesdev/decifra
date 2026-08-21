import type { z } from 'zod'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request<S extends z.ZodType>(
  path: string,
  schema: S,
  init?: RequestInit,
): Promise<z.infer<S>> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) {
    throw new Error(`${init?.method ?? 'GET'} ${path} falhou: ${response.status}`)
  }
  return schema.parse(await response.json())
}

export const api = {
  get: <S extends z.ZodType>(path: string, schema: S) => request(path, schema),
  post: <S extends z.ZodType>(path: string, schema: S, body: unknown) =>
    request(path, schema, { method: 'POST', body: JSON.stringify(body) }),
}
