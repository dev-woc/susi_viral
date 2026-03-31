export type AuthUser = {
  id: string;
  name: string;
  email: string | null;
  workspaceName: string | null;
};

export type AuthState = {
  isLoaded: boolean;
  isSignedIn: boolean;
  user: AuthUser | null;
};

export const DEFAULT_AUTH_STATE: AuthState = {
  isLoaded: true,
  isSignedIn: false,
  user: null,
};
