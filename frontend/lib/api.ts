export async function apiGet<T>(
  path: string,
  mockName: string
): Promise<T | null> {
  if (process.env.NEXT_PUBLIC_USE_MOCKS === "true") {
    try {
      const mockData = await import(`@/mocks/${mockName}.json`);
      return (mockData.default ?? mockData) as T;
    } catch {
      return null;
    }
  }

  try {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
    const cleanPath = path.startsWith("/") ? path : `/${path}`;
    const response = await fetch(`${baseUrl}/api/v1${cleanPath}`);
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as T;
  } catch {
    return null;
  }
}
