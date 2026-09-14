import type { ProjectSummary } from "./api";

function clear(container: HTMLElement): void {
  container.innerHTML = "";
}

function emptyItem(container: HTMLElement, text: string): void {
  const item = document.createElement("li");
  item.className = "pv-muted";
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
    button.className = "pv-list-item";
    button.textContent = project.name;
    button.addEventListener("click", () => onOpen(project.id));
    item.append(button);
    container.append(item);
  }
}
