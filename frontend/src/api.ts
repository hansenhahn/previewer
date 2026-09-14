export interface ProjectSummary {
  id: string;
  name: string;
  encoding: string;
  created_at: string;
  updated_at: string;
}

export interface Asset {
  name: string;
  path: string;
}

export interface Screen {
  name: string;
  font: string;
  background: string;
  x: number;
  y: number;
  new_line: number;
}

export interface Manifest {
  format: string;
  version: number;
  name: string;
  encoding: string;
  texts: { source: string; original: string | null };
  fonts: Asset[];
  backgrounds: Asset[];
  screens: Screen[];
  tags: string[];
  matches: string[];
  segments: { start: string[]; end: string[]; separators: string[] } | null;
}

export interface ProjectDetail extends ProjectSummary {
  manifest: Manifest;
}

export interface AtlasGlyph {
  index: number;
  x: number;
  y: number;
  width: number;
  height: number;
  advance: number;
  leading: number;
}

export interface AtlasMetrics {
  line_height: number;
  default_advance: number;
  image: { width: number; height: number; url: string };
  glyphs: Record<string, AtlasGlyph>;
}

export interface LayoutGlyph {
  codepoint: number;
  index: number;
  x: number;
  y: number;
}

export interface AuthConfig {
  provider: string;
  label: string;
  login_url: string;
}

export interface AuthUser {
  id: string;
  login: string;
  email: string | null;
  avatar_url: string | null;
}

export interface AuthState {
  authenticated: boolean;
  user?: AuthUser;
}

export interface GithubRepo {
  provider: string;
  full_name: string;
  default_branch: string;
  fork: boolean;
  manifest_ok: boolean | null;
  manifest_error: string | null;
}

export function apiUrl(path: string): string {
  return `/api${path}`;
}

export async function listGithubRepos(): Promise<GithubRepo[]> {
  const body = await request<{ repositories: GithubRepo[] }>("/api/github/repos");
  return body.repositories;
}

export async function refreshGithubRepos(): Promise<GithubRepo[]> {
  const body = await request<{ repositories: GithubRepo[] }>(
    "/api/github/repos/refresh",
    { method: "POST" },
  );
  return body.repositories;
}

export function importGithubProject(fullName: string): Promise<ProjectSummary> {
  return request<ProjectSummary>(apiUrl("/projects/github"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ full_name: fullName }),
  });
}

export function getAuthConfig(): Promise<AuthConfig> {
  return request<AuthConfig>("/auth/config");
}

export function getAuthMe(): Promise<AuthState> {
  return request<AuthState>("/auth/me");
}

export function atlasImageUrl(projectId: string, font: string): string {
  return apiUrl(
    `/projects/${encodeURIComponent(projectId)}/fonts/${encodeURIComponent(font)}/atlas.png`,
  );
}

export function backgroundUrl(projectId: string, name: string): string {
  return apiUrl(
    `/projects/${encodeURIComponent(projectId)}/backgrounds/${encodeURIComponent(name)}`,
  );
}

function encodePath(path: string): string {
  return path.split("/").map(encodeURIComponent).join("/");
}

async function request<T>(input: string, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
  if (!response.ok) {
    let message = `erro ${response.status}`;
    try {
      const body = await response.json();
      if (body?.error?.message) {
        message = body.error.message;
      }
    } catch {
      // resposta sem JSON: mantém a mensagem padrão
    }
    throw new Error(message);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export async function listProjects(): Promise<ProjectSummary[]> {
  const body = await request<{ projects: ProjectSummary[] }>(apiUrl("/projects"));
  return body.projects;
}

export function getProject(projectId: string): Promise<ProjectDetail> {
  return request<ProjectDetail>(apiUrl(`/projects/${encodeURIComponent(projectId)}`));
}

export async function uploadProject(file: File): Promise<ProjectSummary> {
  const form = new FormData();
  form.append("file", file);
  return request<ProjectSummary>(apiUrl("/projects"), { method: "POST", body: form });
}

export async function listFiles(projectId: string): Promise<string[]> {
  const body = await request<{ files: string[] }>(
    apiUrl(`/projects/${encodeURIComponent(projectId)}/files`),
  );
  return body.files;
}

export type FileVariant = "source" | "original";

export function fileUrl(
  projectId: string,
  path: string,
  variant: FileVariant = "source",
): string {
  const base = apiUrl(
    `/projects/${encodeURIComponent(projectId)}/files/${encodePath(path)}`,
  );
  return variant === "original" ? `${base}?variant=original` : base;
}

export function readFile(
  projectId: string,
  path: string,
  variant: FileVariant = "source",
): Promise<{ path: string; content: string; encoding: string; variant: string }> {
  return request(fileUrl(projectId, path, variant));
}

export function saveFile(projectId: string, path: string, content: string): Promise<unknown> {
  return request(apiUrl(`/projects/${encodeURIComponent(projectId)}/files/${encodePath(path)}`), {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
}

export function getAtlas(projectId: string, font: string): Promise<AtlasMetrics> {
  return request<AtlasMetrics>(
    apiUrl(`/projects/${encodeURIComponent(projectId)}/fonts/${encodeURIComponent(font)}/atlas`),
  );
}
