export const apiOrigin = (
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? "http://127.0.0.1:8000" : "")
).replace(/\/$/, "");
export async function browserFetch<T>(path: string): Promise<T> {
  if (!apiOrigin) throw new Error("The data service is not configured yet.");
  let response: Response;
  try {
    response = await fetch(apiOrigin + path, {
      signal: AbortSignal.timeout(25000),
    });
  } catch {
    throw new Error("The data service could not be reached. Please try again.");
  }
  if (!response.ok)
    throw new Error(
      response.status === 422
        ? "Please check your date range and filters."
        : "The data service is temporarily unavailable. Please try again.",
    );
  return response.json() as Promise<T>;
}
export async function serverFetch<T>(path: string): Promise<T> {
  const origin = process.env.FRONTEND_API_URL || apiOrigin;
  if (!origin) throw new Error("Data service not configured");
  const response = await fetch(origin.replace(/\/$/, "") + path, {
    next: { revalidate: 300 },
    signal: AbortSignal.timeout(15000),
  });
  if (!response.ok) throw new Error("Data unavailable");
  return response.json() as Promise<T>;
}
export const number = (v: number | null | undefined, digits = 1) =>
  v == null
    ? "—"
    : v.toLocaleString("en-CA", {
        maximumFractionDigits: digits,
        minimumFractionDigits: digits,
      });
export const month = (v: string) =>
  new Date(v + "T00:00:00Z").toLocaleDateString("en-CA", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
export const timestamp = (v: string | null | undefined) =>
  v
    ? new Date(v).toLocaleString("en-CA", {
        timeZone: "UTC",
        dateStyle: "medium",
        timeStyle: "short",
      }) + " UTC"
    : "Not recorded";
