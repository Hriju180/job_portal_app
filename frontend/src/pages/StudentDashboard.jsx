import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";

const STATUS_COLORS = {
  applied: "bg-slate-100 text-slate-700",
  shortlisted: "bg-blue-100 text-blue-700",
  interview: "bg-amber-100 text-amber-700",
  selected: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
};

export default function StudentDashboard() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.get("/applications/");
        setApplications(data.results || []);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleWithdraw = async (id) => {
    if (!confirm("Withdraw this application?")) return;
    try {
      await api.delete(`/applications/${id}/`);
      setApplications((prev) => prev.filter((a) => a.id !== id));
    } catch {
      alert("Failed to withdraw.");
    }
  };

  const visible = filter
    ? applications.filter((a) => a.status === filter)
    : applications;

  // Counts per status for the summary row.
  const counts = applications.reduce((acc, a) => {
    acc[a.status] = (acc[a.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-2xl font-semibold text-slate-800 mb-4">My Applications</h1>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        {["applied", "shortlisted", "interview", "selected", "rejected"].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(filter === s ? "" : s)}
            className={`text-left p-3 rounded shadow-sm border ${
              filter === s ? "border-blue-500" : "border-transparent"
            } bg-white`}
          >
            <div className="text-xs uppercase text-slate-500">{s}</div>
            <div className="text-xl font-semibold text-slate-800">
              {counts[s] || 0}
            </div>
          </button>
        ))}
      </div>

      {loading && <p className="text-slate-500">Loading…</p>}
      {!loading && visible.length === 0 && (
        <p className="text-slate-500">
          No applications yet. <Link to="/jobs" className="text-blue-600">Browse jobs</Link>.
        </p>
      )}

      <div className="space-y-3">
        {visible.map((a) => (
          <div
            key={a.id}
            className="bg-white rounded shadow p-4 flex justify-between items-center"
          >
            <div>
              <Link
                to={`/jobs/${a.job_id}`}
                className="font-semibold text-slate-800 hover:underline"
              >
                {a.job_title}
              </Link>
              <p className="text-sm text-slate-500">
                {a.job_company} · Applied {new Date(a.applied_at).toLocaleDateString()}
              </p>
            </div>

            <div className="flex items-center gap-3">
              <span
                className={`text-xs px-2 py-1 rounded uppercase ${STATUS_COLORS[a.status]}`}
              >
                {a.status}
              </span>
              <button
                onClick={() => handleWithdraw(a.id)}
                className="text-sm text-red-600 hover:underline"
              >
                Withdraw
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}