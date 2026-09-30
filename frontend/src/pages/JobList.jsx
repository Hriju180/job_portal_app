import { useEffect, useState } from "react";
import api from "../api/client";
import JobCard from "../components/JobCard";

export default function JobList() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filter state — drives the query string.
  const [filters, setFilters] = useState({
    search: "",
    location: "",
    job_type: "",
  });

  // Debounced fetch: whenever filters change, refetch after a short delay.
  // Prevents hammering the API on every keystroke.
  useEffect(() => {
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        // Build query string from non-empty filters.
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([k, v]) => {
          if (v) params.append(k, v);
        });

        const { data } = await api.get(`/jobs/?${params.toString()}`);
        // DRF returns a paginated envelope: { count, results, next, previous }
        setJobs(data.results || []);
      } finally {
        setLoading(false);
      }
    }, 400);

    return () => clearTimeout(timer);
  }, [filters]);

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-2xl font-semibold text-slate-800 mb-4">Browse Jobs</h1>

      {/* Filter bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        <input
          placeholder="Search title, company…"
          className="border border-slate-300 rounded px-3 py-2"
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />
        <input
          placeholder="Location"
          className="border border-slate-300 rounded px-3 py-2"
          value={filters.location}
          onChange={(e) => setFilters({ ...filters, location: e.target.value })}
        />
        <select
          className="border border-slate-300 rounded px-3 py-2"
          value={filters.job_type}
          onChange={(e) => setFilters({ ...filters, job_type: e.target.value })}
        >
          <option value="">All types</option>
          <option value="full_time">Full Time</option>
          <option value="intern">Internship</option>
          <option value="part_time">Part Time</option>
          <option value="contract">Contract</option>
        </select>
      </div>

      {loading && <p className="text-slate-500">Loading…</p>}

      {!loading && jobs.length === 0 && (
        <p className="text-slate-500">No jobs match your filters.</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </div>
    </div>
  );
}