import {
  importGithubProject,
  listGithubRepos,
  refreshGithubRepos,
  type GithubRepo,
} from "../api";
import { kit } from "../ui";

export interface GithubImportOptions {
  onImported: (projectId: string) => void;
}

export interface GithubImportHandle {
  element: HTMLElement;
  open(): void;
}

export function createGithubImport(options: GithubImportOptions): GithubImportHandle {
  const modal = document.createElement("div");
  modal.className = "pv-modal";
  modal.hidden = true;

  const dialog = document.createElement("div");
  dialog.className = "pv-modal-dialog";
  dialog.setAttribute("role", "dialog");
  dialog.setAttribute("aria-modal", "true");
  dialog.setAttribute("aria-label", "Importar do GitHub");

  const head = document.createElement("div");
  head.className = "pv-modal-head";
  const title = document.createElement("h2");
  title.textContent = "Importar do GitHub";

  const actions = document.createElement("div");
  actions.className = "pv-github-actions";
  const refresh = iconButton("arrows-rotate", "Atualizar", () => void load(true));
  const close = iconButton("xmark", "Fechar", () => closeModal());
  actions.append(refresh, close);
  head.append(title, actions);

  const status = document.createElement("p");
  status.className = "pv-github-status";

  const list = document.createElement("div");
  list.className = "pv-github-list";

  dialog.append(head, status, list);
  modal.append(dialog);
  modal.addEventListener("mousedown", (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) {
      closeModal();
    }
  });

  function iconButton(name: string, label: string, onClick: () => void): HTMLButtonElement {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "pv-icon-btn";
    button.title = label;
    button.setAttribute("aria-label", label);
    button.append(kit.icon(name, label));
    button.addEventListener("click", onClick);
    return button;
  }

  function closeModal(): void {
    modal.hidden = true;
  }

  function setBusy(busy: boolean): void {
    refresh.disabled = busy;
  }

  function renderRepos(repos: GithubRepo[]): void {
    list.replaceChildren();
    if (repos.length === 0) {
      status.textContent = "Nenhum repositório público encontrado na sua conta.";
      return;
    }
    const usable = repos.filter((repo) => repo.manifest_ok === true).length;
    status.textContent =
      `${usable} de ${repos.length} repositórios têm manifest válido e podem ser importados.`;
    for (const repo of repos) {
      list.append(renderRow(repo));
    }
  }

  function renderRow(repo: GithubRepo): HTMLElement {
    const importable = repo.manifest_ok === true;
    const row = document.createElement("div");
    row.className = importable ? "pv-github-row" : "pv-github-row pv-github-row--disabled";
    if (!importable) {
      row.title = repo.manifest_error ?? "sem manifest válido";
    }

    const info = document.createElement("div");
    info.className = "pv-github-info";
    const name = document.createElement("div");
    name.className = "pv-github-name";
    const label = document.createElement("span");
    label.textContent = repo.full_name;
    name.append(label);
    if (repo.private) {
      name.append(kit.icon("lock", "privado"));
      name.title = "repositório privado";
    }
    const meta = document.createElement("div");
    meta.className = "pv-github-meta";
    const branch = repo.fork ? `fork · ${repo.default_branch}` : repo.default_branch;
    meta.textContent = importable
      ? branch
      : `${branch} · ${repo.manifest_error ?? "sem manifest válido"}`;
    info.append(name, meta);

    const right = document.createElement("div");
    right.className = "pv-github-right";
    const chip = document.createElement("span");
    chip.className = importable ? "pv-github-chip pv-github-chip--ok" : "pv-github-chip pv-github-chip--no";
    chip.textContent = importable ? "✓ importável" : "● sem manifest";
    right.append(chip);

    if (importable) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "pv-github-import";
      button.textContent = "Importar";
      button.addEventListener("click", () => {
        void runImport(repo);
      });
      right.append(button);
    }

    row.append(info, right);
    return row;
  }

  async function runImport(repo: GithubRepo): Promise<void> {
    setBusy(true);
    status.textContent = `Importando ${repo.full_name}…`;
    for (const button of list.querySelectorAll("button")) {
      button.disabled = true;
    }
    try {
      const project = await importGithubProject(repo.full_name);
      closeModal();
      options.onImported(project.id);
    } catch (error) {
      status.textContent = error instanceof Error ? error.message : String(error);
      setBusy(false);
      for (const button of list.querySelectorAll("button")) {
        button.disabled = false;
      }
    }
  }

  async function load(force: boolean): Promise<void> {
    setBusy(true);
    status.textContent = force ? "Atualizando repositórios…" : "Carregando repositórios…";
    list.replaceChildren();
    try {
      let repos = force ? await refreshGithubRepos() : await listGithubRepos();
      if (!force && repos.length === 0) {
        status.textContent = "Buscando repositórios no GitHub…";
        repos = await refreshGithubRepos();
      }
      renderRepos(repos);
    } catch (error) {
      status.textContent = error instanceof Error ? error.message : String(error);
    } finally {
      setBusy(false);
    }
  }

  async function open(): Promise<void> {
    modal.hidden = false;
    await load(false);
  }

  return { element: modal, open: () => void open() };
}
