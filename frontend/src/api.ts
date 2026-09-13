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

export function apiUrl(path: string): string {
  return `/api${path}`;
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

export function readFile(
  projectId: string,
  path: string,
): Promise<{ path: string; content: string; encoding: string }> {
  return request(apiUrl(`/projects/${encodeURIComponent(projectId)}/files/${encodePath(path)}`));
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
