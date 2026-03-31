"use client";

import { createContext, useContext, type ReactNode } from "react";

import { DEFAULT_AUTH_STATE, type AuthState } from "@/lib/auth";

const AuthContext = createContext<AuthState>(DEFAULT_AUTH_STATE);

type AuthProviderProps = {
  children: ReactNode;
  initialState?: Partial<AuthState>;
};

export function AuthProvider({ children, initialState }: AuthProviderProps) {
  const value: AuthState = {
    ...DEFAULT_AUTH_STATE,
    ...initialState,
    user: initialState?.user ?? DEFAULT_AUTH_STATE.user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  return useContext(AuthContext);
}

export function SignedIn({ children }: { children: ReactNode }) {
  const auth = useAuth();
  return auth.isSignedIn ? <>{children}</> : null;
}

export function SignedOut({ children }: { children: ReactNode }) {
  const auth = useAuth();
  return auth.isSignedIn ? null : <>{children}</>;
}
