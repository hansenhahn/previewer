import type { OpenDocument } from "../documents";
import { classNames } from "../ui";

export function renderTabs(
  container: HTMLElement,
  documents: OpenDocument[],
  activePath: string | undefined,
  onSelect: (path: string) => void,
  onClose: (path: string) => void,
): void {
  container.replaceChildren();
  if (documents.length === 0) {
    const empty = document.createElement("span");
    empty.className = "pv-muted";
    empty.textContent = "nenhum arquivo aberto";
    container.append(empty);
    return;
  }

  for (const doc of documents) {
    const tab = document.createElement("div");
    tab.className = classNames("pv-tab", doc.path === activePath && "active");

    const label = document.createElement("button");
    label.type = "button";
    label.className = "pv-tab-label";
    label.textContent = doc.path.split("/").pop() ?? doc.path;
    label.title = doc.path;
    label.addEventListener("click", () => onSelect(doc.path));
    if (doc.modified) {
      const dot = document.createElement("span");
      dot.className = "pv-tab-dot";
      dot.textContent = "●";
      dot.title = "não salvo";
      label.append(dot);
    }

    const close = document.createElement("button");
    close.type = "button";
    close.className = "pv-tab-close";
    close.textContent = "×";
    close.setAttribute("aria-label", `fechar ${doc.path}`);
    close.addEventListener("click", (event) => {
      event.stopPropagation();
      onClose(doc.path);
    });

    tab.append(label, close);
    container.append(tab);
  }
}
