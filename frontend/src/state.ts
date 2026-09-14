import type { AuthConfig, AuthUser, ProjectDetail, ProjectSummary } from "./api";
import type { OpenDocument } from "./documents";

export interface AppState {
  projects: ProjectSummary[];
  project?: ProjectDetail;
  files: string[];
  documents: OpenDocument[];
  activePath?: string;
  currentScreen?: string;
  showOriginal: boolean;
  auth?: AuthUser;
  authConfig?: AuthConfig;
}

export const state: AppState = {
  projects: [],
  files: [],
  documents: [],
  showOriginal: true,
};
