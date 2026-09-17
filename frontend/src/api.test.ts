import { describe, expect, it, vi } from "vitest";

import {
  apiUrl,
  atlasImageUrl,
  backupChange,
  deleteProject,
  discardChange,
  fileUrl,
  getAuthConfig,
  getAuthMe,
  getChangeState,
  importGithubProject,
  listChanges,
  listGithubRepos,
  publishChange,
  resumeChange,
} from "./api";

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

describe("projetos", () => {
  it("remove um projeto", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);
    await deleteProject("a b");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/projects/a%20b",
      expect.objectContaining({ method: "DELETE" }),
    );
    vi.unstubAllGlobals();
  });
});

describe("alterações", () => {
  function respond(payload: unknown, status = 200) {
    return vi.fn().mockImplementation(
      () =>
        new Response(JSON.stringify(payload), {
          status,
          headers: { "Content-Type": "application/json" },
        }),
    );
  }

  it("consulta o estado do chip", async () => {
    const fetchMock = respond({
      branch: "previewer/cap-1",
      status: "draft",
      change: null,
      can_publish: false,
    });
    vi.stubGlobal("fetch", fetchMock);
    const state = await getChangeState("abc");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/projects/abc/changes/state",
      undefined,
    );
    expect(state.status).toBe("draft");
    vi.unstubAllGlobals();
  });

  it("lista as alterações", async () => {
    const fetchMock = respond({ changes: [] });
    vi.stubGlobal("fetch", fetchMock);
    expect(await listChanges("abc")).toEqual([]);
    vi.unstubAllGlobals();
  });

  it("sobe um rascunho com título e descrição", async () => {
    const fetchMock = respond({ id: "c1", pr_number: 12, url: "u", created: true });
    vi.stubGlobal("fetch", fetchMock);
    await publishChange("abc", "c1", "Capítulo 1", "desc");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/projects/abc/changes/c1/publish",
      expect.objectContaining({ method: "POST" }),
    );
    vi.unstubAllGlobals();
  });

  it("faz backup do rascunho", async () => {
    const fetchMock = respond({ id: "c1" });
    vi.stubGlobal("fetch", fetchMock);
    await backupChange("abc", "c1");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/projects/abc/changes/c1/backup",
      expect.objectContaining({ method: "POST" }),
    );
    vi.unstubAllGlobals();
  });

  it("retoma e descarta uma alteração", async () => {
    const fetchMock = respond({ id: "c1" });
    vi.stubGlobal("fetch", fetchMock);
    await resumeChange("abc", "c1");
    await discardChange("abc", "c1");
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/api/projects/abc/changes/c1/resume",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/projects/abc/changes/c1/discard",
      expect.objectContaining({ method: "POST" }),
    );
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
