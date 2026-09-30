// Wraps routes that require authentication.
// Optional `roles` prop restricts by role.
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, roles }) {
  const { user } = useAuth();

  // Not logged in -> go to login.
  if (!user) return <Navigate to="/login" replace />;

  // Role mismatch -> bounce to a safe page for their role.
  if (roles && !roles.includes(user.role)) {
    return <Navigate to={user.role === "recruiter" ? "/recruiter" : "/jobs"} replace />;
  }

  return children;
}