import { describe, expect, it, vi } from "vitest";

import { apiUrl, atlasImageUrl, fileUrl, getAuthConfig, getAuthMe, importGithubProject, listGithubRepos } from "./api";

describe("helpers de URL", () => {
  it("monta a URL do atlas", () => {
    expect(atlasImageUrl("abc", "fontevent")).toBe(
      "/api/projects/abc/fonts/fontevent/atlas.png",
    );
  });

  it("codifica os segmentos", () => {
    expect(atlasImageUrl("a b", "f/x")).toBe(
      "/api/projects/a%20b/fonts/f%2Fx/atlas.png",
    );
  });

  it("monta a URL base da API", () => {
    expect(apiUrl("/projects")).toBe("/api/projects");
  });

  it("monta a URL do arquivo por variante", () => {
    expect(fileUrl("abc", "texts/cap01.txt")).toBe(
      "/api/projects/abc/files/texts/cap01.txt",
    );
    expect(fileUrl("abc", "texts/cap01.txt", "original")).toBe(
      "/api/projects/abc/files/texts/cap01.txt?variant=original",
    );
  });
});

describe("autenticação", () => {
  it("consulta a configuração de entrada sem provedor fixo", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ provider: "fake", label: "Exemplo", login_url: "/auth/login" }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    const config = await getAuthConfig();
    expect(fetchMock).toHaveBeenCalledWith("/auth/config", undefined);
    expect(config.label).toBe("Exemplo");
    vi.unstubAllGlobals();
  });

  it("consulta o estado do usuário atual", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ authenticated: false }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    const state = await getAuthMe();
    expect(fetchMock).toHaveBeenCalledWith("/auth/me", undefined);
    expect(state.authenticated).toBe(false);
    vi.unstubAllGlobals();
  });
});

describe("import do GitHub", () => {
  it("lista os repositórios da conta", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          repositories: [
            {
              provider: "github",
              full_name: "alice/projeto",
              default_branch: "main",
              fork: false,
            },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    const repos = await listGithubRepos();
    expect(fetchMock).toHaveBeenCalledWith("/api/github/repos", undefined);
    expect(repos[0].full_name).toBe("alice/projeto");
    vi.unstubAllGlobals();
  });

  it("importa um repositório", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          id: "1",
          name: "Projeto",
          encoding: "windows-1252",
          created_at: "",
          updated_at: "",
        }),
        { status: 201, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    const project = await importGithubProject("alice/projeto");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/projects/github",
      expect.objectContaining({ method: "POST" }),
    );
    expect(project.id).toBe("1");
    vi.unstubAllGlobals();
  });
});
