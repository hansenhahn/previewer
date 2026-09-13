import type { ProjectDetail, ProjectSummary } from "./api";

export interface AppState {
  projects: ProjectSummary[];
  project?: ProjectDetail;
  files: string[];
  currentPath?: string;
  currentScreen?: string;
}

export const state: AppState = {
  projects: [],
  files: [],
};
