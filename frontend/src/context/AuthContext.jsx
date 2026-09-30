// Global auth state — user object + login/logout helpers.
// Wrapped around the app so any component can call useAuth().
import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Initialise from localStorage so a page refresh doesn't log the user out.
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  });

  const [loading, setLoading] = useState(false);

  // Persist user changes to localStorage.
  useEffect(() => {
    if (user) localStorage.setItem("user", JSON.stringify(user));
    else localStorage.removeItem("user");
  }, [user]);

  // Called after a successful /login or /register response.
  const login = (userData, accessToken, refreshToken) => {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  };

  // Optional: re-fetch the user object from /me/ using the stored token.
  // Useful if the user profile changed on the backend.
  const refreshUser = async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/auth/me/");
      setUser(data);
      return data;
    } finally {
      setLoading(false);
    }
  };

  const value = { user, loading, login, logout, refreshUser };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Convenience hook.
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}