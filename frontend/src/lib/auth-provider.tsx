// Authentication context and provider.

"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { api, getStoredToken, setStoredToken, clearStoredToken } from "./api";
import type { AuthResponse, User } from "@/types";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
  token: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function setAuthCookie(token: string) {
  // Only runs on client to avoid hydration mismatch
  if (typeof window === "undefined") return;

  // Set cookie that expires in 7 days (same as JWT expiration)
  const expires = new Date();
  expires.setDate(expires.getDate() + 7);
  document.cookie = `auth_token=${token};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
}

function clearAuthCookie() {
  document.cookie = "auth_token=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = getStoredToken();
      if (storedToken) {
        try {
          // Decode token to get user info (simplified)
          const payload = JSON.parse(atob(storedToken.split(".")[1]));
          setTokenState(storedToken);
          api.setToken(storedToken);
          setUser({
            id: payload.sub,
            email: payload.email,
          });
        } catch {
          clearStoredToken();
          clearAuthCookie();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.login({ email, password });
    const { access_token, user_id, email: userEmail } = response;

    setStoredToken(access_token);
    setAuthCookie(access_token);
    setTokenState(access_token);
    api.setToken(access_token);

    setUser({
      id: user_id,
      email: userEmail,
    });
  };

  const signup = async (email: string, password: string) => {
    const response = await api.signup({ email, password });
    const { access_token, user_id, email: userEmail } = response;

    setStoredToken(access_token);
    setAuthCookie(access_token);
    setTokenState(access_token);
    api.setToken(access_token);

    setUser({
      id: user_id,
      email: userEmail,
    });
  };

  const logout = () => {
    clearStoredToken();
    clearAuthCookie();
    setTokenState(null);
    api.setToken(null);
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!token,
        login,
        signup,
        logout,
        token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
