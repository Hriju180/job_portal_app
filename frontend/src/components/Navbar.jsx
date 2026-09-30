import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-slate-800 text-white px-6 py-4 flex items-center justify-between">
      <Link to="/" className="font-bold text-lg">Placement Tracker</Link>

      <div className="flex items-center gap-4">
        {!user && (
          <>
            <Link to="/login" className="hover:underline">Login</Link>
            <Link
              to="/register"
              className="bg-blue-600 px-3 py-1 rounded hover:bg-blue-700"
            >
              Register
            </Link>
          </>
        )}

        {user && user.role === "student" && (
          <>
            <Link to="/jobs" className="hover:underline">Jobs</Link>
            <Link to="/student" className="hover:underline">My Applications</Link>
            <Link to="/profile" className="hover:underline">Profile</Link>
          </>
        )}

        {user && user.role === "recruiter" && (
          <>
            <Link to="/recruiter" className="hover:underline">Dashboard</Link>
            <Link to="/profile" className="hover:underline">Profile</Link>
          </>
        )}

        {user && (
          <>
            <span className="text-sm text-slate-300">{user.email}</span>
            <button
              onClick={handleLogout}
              className="bg-red-500 px-3 py-1 rounded hover:bg-red-600"
            >
              Logout
            </button>
          </>
        )}
      </div>
    </nav>
  );
}