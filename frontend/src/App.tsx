
import { useEffect, useState } from "react";
import {
  Activity as ActivityIcon,
  Eye,
  Users,
  MousePointerClick,
  TrendingUp,
  LayoutDashboard,
  FileBarChart,
  Settings,
  RefreshCw
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip
} from "recharts";
import {
  getSummary,
  getTraffic,
  getActivity,
  type DashboardSummary,
  type TrafficPoint,
  type Activity
} from "./api";
import "./App.css";

function App() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [traffic, setTraffic] = useState<TrafficPoint[]>([]);
  const [activity, setActivity] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const [summaryData, trafficData, activityData] = await Promise.all([
        getSummary(),
        getTraffic(),
        getActivity()
      ]);

      setSummary(summaryData);
      setTraffic(trafficData);
      setActivity(activityData);
    } catch {
      setError("Could not load dashboard data. Check whether the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDashboard();
  }, []);

  const cards = summary
    ? [
        {
          title: "Total Users",
          value: summary.totalUsers.toLocaleString(),
          icon: Users
        },
        {
          title: "Active Users",
          value: summary.activeUsers.toLocaleString(),
          icon: ActivityIcon
        },
        {
          title: "Page Views",
          value: summary.pageViews.toLocaleString(),
          icon: Eye
        },
        {
          title: "Sessions",
          value: summary.sessions.toLocaleString(),
          icon: MousePointerClick
        }
      ]
    : [];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><TrendingUp size={22} /></div>
          <span>Insight<span className="brand-light">Flow</span></span>
        </div>

        <p className="nav-label">WORKSPACE</p>
        <nav>
          <a className="nav-item active" href="#overview">
            <LayoutDashboard size={18} /> Overview
          </a>
          <a className="nav-item" href="#traffic">
            <TrendingUp size={18} /> Traffic Analytics
          </a>
          <a className="nav-item" href="#activity">
            <ActivityIcon size={18} /> User Activity
          </a>
          <a className="nav-item" href="#reports">
            <FileBarChart size={18} /> Reports
          </a>
        </nav>

        <div className="sidebar-bottom">
          <a className="nav-item" href="#settings">
            <Settings size={18} /> Settings
          </a>
          <p>Analytics Dashboard v1.0</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">WORKSPACE / OVERVIEW</p>
            <h1>Analytics Overview</h1>
            <p className="subtitle">
              Monitor users, traffic and engagement in one place.
            </p>
          </div>
          <button className="refresh-button" onClick={loadDashboard}>
            <RefreshCw size={16} /> Refresh
          </button>
        </header>

        {error && (
          <div className="error-message">
            {error}
            <button onClick={loadDashboard}>Retry</button>
          </div>
        )}

        {loading && <p className="status-message">Loading dashboard...</p>}

        {!loading && !error && summary && (
          <>
            <section className="metrics-grid" id="overview">
              {cards.map((card) => {
                const Icon = card.icon;
                return (
                  <article className="metric-card" key={card.title}>
                    <div className="metric-heading">
                      <span>{card.title}</span>
                      <span className="metric-icon"><Icon size={19} /></span>
                    </div>
                    <div className="metric-value">{card.value}</div>
                    <p className="metric-footnote">Sample analytics data</p>
                  </article>
                );
              })}
            </section>

            <section className="content-grid">
              <article className="panel traffic-panel" id="traffic">
                <div className="panel-heading">
                  <div>
                    <h2>Traffic Overview</h2>
                    <p>Daily visitors over the last seven sample days</p>
                  </div>
                  <span className="period-badge">7 days</span>
                </div>

                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={traffic}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis
                        dataKey="date"
                        tickFormatter={(date) => date.slice(5)}
                        tickLine={false}
                        axisLine={false}
                      />
                      <YAxis tickLine={false} axisLine={false} />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="visitors"
                        name="Visitors"
                        stroke="#5965e8"
                        strokeWidth={3}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </article>

              <article className="panel engagement-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Engagement</h2>
                    <p>Session quality indicator</p>
                  </div>
                </div>
                <div className="engagement-value">
                  {summary.bounceRate}%
                </div>
                <p className="engagement-label">Bounce rate</p>
                <div className="progress-track">
                  <div
                    className="progress-fill"
                    style={{ width: `${Math.min(100, Math.max(0, summary.bounceRate))}%` }}
                  />
                </div>
                <p className="small-note">
                  Percentage of sessions that leave after a single page view.
                </p>
              </article>
            </section>

            <section className="panel activity-panel" id="activity">
              <div className="panel-heading">
                <div>
                  <h2>Recent User Activity</h2>
                  <p>Latest recorded sample events</p>
                </div>
                <span className="live-indicator">● Sample data</span>
              </div>

              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>User</th>
                      <th>Activity</th>
                      <th>Page</th>
                      <th>Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activity.map((item) => (
                      <tr key={item.id}>
                        <td><strong>{item.user}</strong></td>
                        <td>{item.action}</td>
                        <td><code>{item.page}</code></td>
                        <td>{new Date(item.timestamp).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
