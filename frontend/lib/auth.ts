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

const DEV_BYPASS_USER: AuthUser = {
  id: "dev-user",
  name: "Local User",
  email: null,
  workspaceName: "Default Workspace",
};

export const DEFAULT_AUTH_STATE: AuthState = {
  isLoaded: true,
  isSignedIn: true,
  user: DEV_BYPASS_USER,
};
