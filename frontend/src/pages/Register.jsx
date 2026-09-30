import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    password2: "",
    role: "student",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await api.post("/auth/register/", form);
      login(data.user, data.access, data.refresh);
      navigate(data.user.role === "recruiter" ? "/recruiter" : "/jobs");
    } catch (err) {
      // Flatten DRF error object into a readable string.
      const res = err.response?.data;
      const msg =
        typeof res === "string"
          ? res
          : res
          ? Object.values(res).flat().join(" ")
          : "Registration failed.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 p-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-6 rounded-lg shadow w-full max-w-sm"
      >
        <h2 className="text-xl font-semibold mb-4 text-slate-800">Register</h2>

        {error && (
          <div className="bg-red-50 text-red-600 text-sm p-2 rounded mb-3">
            {error}
          </div>
        )}

        <input
          type="email"
          placeholder="Email"
          className="w-full border border-slate-300 rounded px-3 py-2 mb-3"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="Username"
          className="w-full border border-slate-300 rounded px-3 py-2 mb-3"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          required
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full border border-slate-300 rounded px-3 py-2 mb-3"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          required
        />
        <input
          type="password"
          placeholder="Confirm Password"
          className="w-full border border-slate-300 rounded px-3 py-2 mb-3"
          value={form.password2}
          onChange={(e) => setForm({ ...form, password2: e.target.value })}
          required
        />

        <select
          className="w-full border border-slate-300 rounded px-3 py-2 mb-4"
          value={form.role}
          onChange={(e) => setForm({ ...form, role: e.target.value })}
        >
          <option value="student">Student</option>
          <option value="recruiter">Recruiter</option>
        </select>

        <button
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-60"
        >
          {loading ? "Creating account…" : "Register"}
        </button>

        <p className="text-sm text-slate-500 mt-4 text-center">
          Already registered?{" "}
          <Link to="/login" className="text-blue-600 hover:underline">
            Log in
          </Link>
        </p>
      </form>
    </div>
  );
}