import type { ProjectSummary } from "./api";

function clear(container: HTMLElement): void {
  container.innerHTML = "";
}

function emptyItem(container: HTMLElement, text: string): void {
  const item = document.createElement("li");
  item.className = "muted";
  item.textContent = text;
  container.append(item);
}

export function renderProjectList(
  container: HTMLElement,
  projects: ProjectSummary[],
  onOpen: (id: string) => void,
): void {
  clear(container);
  if (projects.length === 0) {
    emptyItem(container, "nenhum projeto");
    return;
  }
  for (const project of projects) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.textContent = project.name;
    button.addEventListener("click", () => onOpen(project.id));
    item.append(button);
    container.append(item);
  }
}

export function renderFileList(
  container: HTMLElement,
  files: string[],
  current: string | undefined,
  onSelect: (path: string) => void,
): void {
  clear(container);
  if (files.length === 0) {
    emptyItem(container, "nenhum arquivo");
    return;
  }
  for (const path of files) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.textContent = path;
    if (path === current) {
      button.classList.add("active");
    }
    button.addEventListener("click", () => onSelect(path));
    item.append(button);
    container.append(item);
  }
}

export function showError(message: string | undefined): void {
  const element = document.getElementById("error");
  if (!element) {
    return;
  }
  element.textContent = message ?? "";
  element.hidden = !message;
}
