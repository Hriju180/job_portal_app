import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function JobDetail() {
  const { id } = useParams();
  const { user } = useAuth();

  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [coverNote, setCoverNote] = useState("");
  const [message, setMessage] = useState("");
  const [applying, setApplying] = useState(false);
  const [alreadyApplied, setAlreadyApplied] = useState(false);

  // Load job.
  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.get(`/jobs/${id}/`);
        setJob(data);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  // If student, check whether they already applied.
  useEffect(() => {
    if (!user || user.role !== "student") return;
    const check = async () => {
      try {
        const { data } = await api.get("/applications/");
        const mine = (data.results || []).some((a) => a.job_id === Number(id));
        setAlreadyApplied(mine);
      } catch {
        // ignore
      }
    };
    check();
  }, [id, user]);

  const handleApply = async () => {
    setMessage("");
    setApplying(true);
    try {
      await api.post("/applications/", {
        job: Number(id),
        cover_note: coverNote,
      });
      setMessage("Application submitted successfully.");
      setAlreadyApplied(true);
    } catch (err) {
      const res = err.response?.data;
      const msg =
        typeof res === "string"
          ? res
          : res
          ? Object.values(res).flat().join(" ")
          : "Application failed.";
      setMessage(msg);
    } finally {
      setApplying(false);
    }
  };

  if (loading) return <p className="p-6 text-slate-500">Loading…</p>;
  if (!job) return <p className="p-6 text-red-600">Job not found.</p>;

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-semibold text-slate-800">{job.title}</h1>
      <p className="text-slate-500 mb-1">
        {job.company_name || job.recruiter_username} · {job.location}
      </p>
      <p className="text-slate-600 mb-4">{job.package || "Not specified"}</p>

      <div className="flex flex-wrap gap-2 mb-4">
        {(job.skills_required || []).map((s) => (
          <span key={s} className="text-xs bg-slate-100 px-2 py-1 rounded">
            {s}
          </span>
        ))}
      </div>

      <div className="bg-white p-5 rounded shadow mb-6">
        <h2 className="font-semibold mb-2 text-slate-800">Description</h2>
        <p className="whitespace-pre-line text-slate-700">{job.description}</p>
      </div>

      {job.deadline && (
        <p className="text-sm text-slate-500 mb-4">
          Application deadline: {job.deadline}
        </p>
      )}

      {user?.role === "student" && (
        <div className="bg-white p-5 rounded shadow">
          <h2 className="font-semibold mb-3 text-slate-800">Apply</h2>

          {alreadyApplied ? (
            <p className="text-green-600 text-sm">You have already applied to this job.</p>
          ) : (
            <>
              <textarea
                placeholder="Optional cover note…"
                className="w-full border border-slate-300 rounded px-3 py-2 mb-3"
                rows={3}
                value={coverNote}
                onChange={(e) => setCoverNote(e.target.value)}
              />
              <button
                onClick={handleApply}
                disabled={applying}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-60"
              >
                {applying ? "Submitting…" : "Submit Application"}
              </button>
            </>
          )}

          {message && <p className="text-sm text-slate-700 mt-3">{message}</p>}
        </div>
      )}

      {user?.role === "recruiter" && (
        <p className="text-sm text-slate-500">
          Only students can apply to jobs.
        </p>
      )}
    </div>
  );
}