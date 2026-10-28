const API_URL = import.meta.env.VITE_API_URL;

export interface DashboardSummary {
  totalUsers: number;
  activeUsers: number;
  pageViews: number;
  sessions: number;
  bounceRate: number;
}

export interface TrafficPoint {
  date: string;
  visitors: number;
}

export interface Activity {
  id: number;
  user: string;
  action: string;
  page: string;
  timestamp: string;
}

async function fetchApi<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const getSummary = () =>
  fetchApi<DashboardSummary>("/api/dashboard/summary");

export const getTraffic = () =>
  fetchApi<TrafficPoint[]>("/api/dashboard/traffic");

export const getActivity = () =>
  fetchApi<Activity[]>("/api/dashboard/activity");