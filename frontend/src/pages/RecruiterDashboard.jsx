import { useEffect, useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

const JOB_TYPES = [
  { value: "full_time", label: "Full Time" },
  { value: "intern", label: "Internship" },
  { value: "part_time", label: "Part Time" },
  { value: "contract", label: "Contract" },
];

export default function RecruiterDashboard() {
  const { user } = useAuth();

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [applicants, setApplicants] = useState({}); // jobId -> array
  const [expanded, setExpanded] = useState(null);   // which job's applicants are visible

  // ---- Create-job form state -------------------------------------------
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    title: "",
    description: "",
    location: "",
    job_type: "full_time",
    package: "",
    skills: "",        // comma-separated string; converted to array on submit
    deadline: "",
  });
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // ---- Load my jobs ----------------------------------------------------
  const loadJobs = async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/jobs/?page_size=100");
      // Filter client-side: only jobs whose recruiter_username matches me.
      const mine = (data.results || []).filter(
        (j) => j.recruiter_username === user?.username
      );
      setJobs(mine);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) loadJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // ---- Toggle applicants view ------------------------------------------
  const toggleApplicants = async (jobId) => {
    if (expanded === jobId) {
      setExpanded(null);
      return;
    }
    setExpanded(jobId);

    // Only fetch once; cache afterward.
    if (!applicants[jobId]) {
      const { data } = await api.get(`/applications/job/${jobId}/`);
      setApplicants((prev) => ({
        ...prev,
        [jobId]: data.results || data,
      }));
    }
  };

  // ---- Update an applicant's status ------------------------------------
  const updateStatus = async (applicationId, jobId, newStatus) => {
    try {
      const { data } = await api.patch(
        `/applications/${applicationId}/status/`,
        { status: newStatus }
      );
      setApplicants((prev) => ({
        ...prev,
        [jobId]: prev[jobId].map((a) => (a.id === applicationId ? data : a)),
      }));
    } catch {
      alert("Failed to update status.");
    }
  };

  // ---- Create a new job -------------------------------------------------
  const handleCreateJob = async (e) => {
    e.preventDefault();
    setFormError("");
    setSubmitting(true);

    try {
      // Convert comma-separated skills string into a clean array.
      const skillsArray = form.skills
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      const payload = {
        title: form.title,
        description: form.description,
        location: form.location,
        job_type: form.job_type,
        package: form.package,
        skills_required: skillsArray,
        deadline: form.deadline || null,
        is_active: true,
      };

      await api.post("/jobs/", payload);

      // Reset the form and close it.
      setForm({
        title: "",
        description: "",
        location: "",
        job_type: "full_time",
        package: "",
        skills: "",
        deadline: "",
      });
      setShowForm(false);

      // Refetch the list so the new job appears.
      await loadJobs();
    } catch (err) {
      const res = err.response?.data;
      const msg =
        typeof res === "string"
          ? res
          : res
          ? Object.entries(res)
              .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
              .join(" | ")
          : "Failed to create job.";
      setFormError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <p className="p-6 text-slate-500">Loading…</p>;

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold text-slate-800">My Jobs</h1>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {showForm ? "Cancel" : "+ Post a Job"}
        </button>
      </div>

      {/* ---- Create form ---- */}
      {showForm && (
        <form
          onSubmit={handleCreateJob}
          className="bg-white rounded shadow p-5 mb-6 space-y-3"
        >
          <h2 className="font-semibold text-slate-800 mb-1">New Job Post</h2>

          {formError && (
            <div className="bg-red-50 text-red-600 text-sm p-2 rounded">
              {formError}
            </div>
          )}

          <input
            placeholder="Job title *"
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="w-full border border-slate-300 rounded px-3 py-2"
          />

          <textarea
            placeholder="Description *"
            required
            rows={4}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className="w-full border border-slate-300 rounded px-3 py-2"
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input
              placeholder="Location *"
              required
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
              className="w-full border border-slate-300 rounded px-3 py-2"
            />
            <select
              value={form.job_type}
              onChange={(e) => setForm({ ...form, job_type: e.target.value })}
              className="w-full border border-slate-300 rounded px-3 py-2"
            >
              {JOB_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input
              placeholder="Package (e.g. 8 LPA, ₹25,000/month)"
              value={form.package}
              onChange={(e) => setForm({ ...form, package: e.target.value })}
              className="w-full border border-slate-300 rounded px-3 py-2"
            />
            <input
              type="date"
              value={form.deadline}
              onChange={(e) => setForm({ ...form, deadline: e.target.value })}
              className="w-full border border-slate-300 rounded px-3 py-2"
            />
          </div>

          <input
            placeholder="Skills (comma separated, e.g. Python, Django, React)"
            value={form.skills}
            onChange={(e) => setForm({ ...form, skills: e.target.value })}
            className="w-full border border-slate-300 rounded px-3 py-2"
          />

          <button
            type="submit"
            disabled={submitting}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-60"
          >
            {submitting ? "Posting…" : "Post Job"}
          </button>
        </form>
      )}

      {/* ---- My jobs list ---- */}
      {jobs.length === 0 && !showForm && (
        <p className="text-slate-500">
          You haven't posted any jobs yet. Click <b>+ Post a Job</b> to create one.
        </p>
      )}

      <div className="space-y-4">
        {jobs.map((job) => (
          <div key={job.id} className="bg-white rounded shadow">
            <div className="p-4 flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-slate-800">{job.title}</h3>
                <p className="text-sm text-slate-500">
                  {job.location} · {job.job_type.replace("_", " ")} ·{" "}
                  {job.is_active ? (
                    <span className="text-green-600">Active</span>
                  ) : (
                    <span className="text-red-500">Inactive</span>
                  )}
                </p>
              </div>
              <button
                onClick={() => toggleApplicants(job.id)}
                className="text-blue-600 hover:underline text-sm"
              >
                {expanded === job.id ? "Hide applicants" : "View applicants"}
              </button>
            </div>

            {expanded === job.id && (
              <div className="border-t">
                {(applicants[job.id] || []).length === 0 ? (
                  <p className="p-4 text-slate-500 text-sm">No applicants yet.</p>
                ) : (
                  applicants[job.id].map((a) => (
                    <div
                      key={a.id}
                      className="p-4 border-b last:border-b-0 flex flex-col md:flex-row md:justify-between md:items-center gap-3"
                    >
                      <div>
                        <p className="font-medium text-slate-800">
                          {a.student_username} · {a.student_email}
                        </p>
                        {a.cover_note && (
                          <p className="text-sm text-slate-500 mt-1">
                            {a.cover_note}
                          </p>
                        )}
                        {a.resume && (
                          <a
                            href={a.resume}
                            target="_blank"
                            rel="noreferrer"
                            className="text-xs text-blue-600 hover:underline"
                          >
                            View resume
                          </a>
                        )}
                      </div>

                      <select
                        value={a.status}
                        onChange={(e) => updateStatus(a.id, job.id, e.target.value)}
                        className="border border-slate-300 rounded px-2 py-1 text-sm self-start md:self-auto"
                      >
                        <option value="applied">Applied</option>
                        <option value="shortlisted">Shortlisted</option>
                        <option value="interview">Interview</option>
                        <option value="selected">Selected</option>
                        <option value="rejected">Rejected</option>
                      </select>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}