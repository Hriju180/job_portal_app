import { useEffect, useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [message, setMessage] = useState("");
  const [uploading, setUploading] = useState(false);

  const isStudent = user?.role === "student";
  const endpoint = isStudent ? "/auth/profile/student/" : "/auth/profile/recruiter/";

  useEffect(() => {
    const load = async () => {
      const { data } = await api.get(endpoint);
      setProfile(data);
    };
    load();
  }, [endpoint]);

  const handleChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setMessage("");
    try {
      const payload = { ...profile };
      delete payload.email;
      delete payload.username;
      delete payload.updated_at;
      delete payload.resume;
      delete payload.company_logo;

      const { data } = await api.put(endpoint, payload);
      setProfile(data);
      setMessage("Profile saved.");
    } catch {
      setMessage("Failed to save.");
    }
  };

  const handleResumeUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("resume", file);
    setUploading(true);
    try {
      const { data } = await api.post("/auth/profile/resume/", fd);
      setProfile(data);
      setMessage("Resume uploaded.");
    } catch (err) {
      setMessage(err.response?.data?.resume?.[0] || "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  if (!profile) return <p className="p-6 text-slate-500">Loading…</p>;

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-semibold text-slate-800 mb-4">My Profile</h1>

      {message && (
        <div className="bg-blue-50 text-blue-700 text-sm p-2 rounded mb-3">
          {message}
        </div>
      )}

      <form onSubmit={handleSave} className="bg-white rounded shadow p-5 space-y-3">
        <div>
          <label className="text-xs text-slate-500">Email</label>
          <input
            disabled
            value={profile.email}
            className="w-full border border-slate-200 bg-slate-50 rounded px-3 py-2"
          />
        </div>

        {isStudent && (
          <>
            <input name="phone" placeholder="Phone" value={profile.phone || ""}
              onChange={handleChange}
              className="w-full border border-slate-300 rounded px-3 py-2" />
            <textarea name="bio" placeholder="Bio" value={profile.bio || ""}
              onChange={handleChange} rows={3}
              className="w-full border border-slate-300 rounded px-3 py-2" />
            <input name="degree" placeholder="Degree" value={profile.degree || ""}
              onChange={handleChange}
              className="w-full border border-slate-300 rounded px-3 py-2" />
            <input name="college" placeholder="College" value={profile.college || ""}
              onChange={handleChange}
              className="w-full border border-slate-300 rounded px-3 py-2" />
            <input name="cgpa" placeholder="CGPA" value={profile.cgpa || ""}
              onChange={handleChange}
              className="w-full border border-slate-300 rounded px-3 py-2" />
            <input name="graduation_year" type="number" placeholder="Graduation year"
              value={profile.graduation_year || ""}
              onChange={handleChange}
              className="w-full border border-slate-300 rounded px-3 py-2" />
          </>
        )}

        {!isStudent && (
          <>
            <input name="company_name" placeholder="Company name" value={profile.company_name || ""}
              onChange={handleChange}
              className="w-full border border-slate-300 rounded px-3 py-2" />
            <input name="company_website" placeholder="Company website" value={profile.company_website || ""}
              onChange={handleChange}
              className="w-full border border-slate-300 rounded px-3 py-2" />
            <input name="designation" placeholder="Designation" value={profile.designation || ""}
              onChange={handleChange}
              className="w-full border border-slate-300 rounded px-3 py-2" />
          </>
        )}

        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Save
        </button>
      </form>

      {isStudent && (
        <div className="bg-white rounded shadow p-5 mt-4">
          <h2 className="font-semibold text-slate-800 mb-2">Resume</h2>
          {profile.resume ? (
            <a href={profile.resume} target="_blank" rel="noreferrer"
              className="text-blue-600 hover:underline text-sm">
              View current resume
            </a>
          ) : (
            <p className="text-sm text-slate-500 mb-2">No resume uploaded.</p>
          )}
          <input
            type="file"
            accept=".pdf"
            onChange={handleResumeUpload}
            disabled={uploading}
            className="mt-3 block"
          />
        </div>
      )}
    </div>
  );
}