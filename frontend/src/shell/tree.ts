import { classNames, kit } from "../ui";

export interface TreeEntry {
  display: string;
  path: string;
}

export interface TreeNode {
  name: string;
  path?: string;
  children: TreeNode[];
}

export function stripPrefix(path: string, prefix: string): string {
  return prefix && path.startsWith(prefix) ? path.slice(prefix.length) : path;
}

export function buildTree(entries: TreeEntry[]): TreeNode[] {
  const root: TreeNode = { name: "", children: [] };

  for (const entry of entries) {
    const parts = entry.display.split("/").filter(Boolean);
    let node = root;
    parts.forEach((part, index) => {
      const isFile = index === parts.length - 1;
      let child = node.children.find(
        (candidate) => candidate.name === part && (isFile ? candidate.path : !candidate.path),
      );
      if (!child) {
        child = { name: part, children: [], path: isFile ? entry.path : undefined };
        node.children.push(child);
      }
      node = child;
    });
  }

  const sortNodes = (nodes: TreeNode[]): void => {
    nodes.sort((a, b) => {
      const aFolder = a.path ? 1 : 0;
      const bFolder = b.path ? 1 : 0;
      if (aFolder !== bFolder) {
        return aFolder - bFolder;
      }
      return a.name.localeCompare(b.name);
    });
    nodes.forEach((node) => sortNodes(node.children));
  };
  sortNodes(root.children);
  return root.children;
}

function renderNodes(
  container: HTMLElement,
  nodes: TreeNode[],
  activePath: string | undefined,
  onSelect: (path: string) => void,
): void {
  const list = document.createElement("ul");
  list.className = "pv-tree";

  for (const node of nodes) {
    const item = document.createElement("li");

    if (node.path) {
      const row = document.createElement("div");
      row.className = classNames("pv-tree-item", node.path === activePath && "active");
      row.setAttribute("role", "treeitem");
      row.tabIndex = 0;
      const label = document.createElement("span");
      label.textContent = node.name;
      row.append(kit.icon("file-lines"), label);
      row.addEventListener("click", () => onSelect(node.path as string));
      row.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onSelect(node.path as string);
        }
      });
      item.append(row);
    } else {
      const details = document.createElement("details");
      details.open = true;
      const summary = document.createElement("summary");
      summary.className = "pv-tree-item pv-tree-folder";
      const label = document.createElement("span");
      label.textContent = node.name;
      summary.append(kit.icon("folder"), label);
      details.append(summary);
      const children = document.createElement("div");
      children.className = "pv-tree-children";
      renderNodes(children, node.children, activePath, onSelect);
      details.append(children);
      item.append(details);
    }

    list.append(item);
  }

  container.append(list);
}

export function renderFileTree(
  container: HTMLElement,
  files: string[],
  prefix: string,
  activePath: string | undefined,
  onSelect: (path: string) => void,
): void {
  container.replaceChildren();
  if (files.length === 0) {
    const empty = document.createElement("p");
    empty.className = "pv-muted";
    empty.textContent = "nenhum arquivo";
    container.append(empty);
    return;
  }
  const entries = files.map((path) => ({ display: stripPrefix(path, prefix), path }));
  renderNodes(container, buildTree(entries), activePath, onSelect);
}
