/** Read at request time — module-level process.env is baked in at `next build`. */
export function getApiUrl(): string {
  return (process.env.API_URL ?? "http://localhost:8000").replace(/\/$/, "");
}
