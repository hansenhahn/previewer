import {
  getProject,
  listFiles,
  listProjects,
  readFile,
  saveFile,
  uploadProject,
} from "./api";
import { createEditor } from "./editor";
import { Preview } from "./preview";
import { renderFileList, renderProjectList, showError } from "./ui";
import { state } from "./state";

function element<T extends HTMLElement>(id: string): T {
  const found = document.getElementById(id);
  if (!found) {
    throw new Error(`elemento ausente: ${id}`);
  }
  return found as T;
}

const projectList = element<HTMLUListElement>("project-list");
const fileList = element<HTMLUListElement>("file-list");
const screenSelect = element<HTMLSelectElement>("screen-select");
const zoom = element<HTMLInputElement>("zoom");
const status = element<HTMLSpanElement>("status");
const upload = element<HTMLInputElement>("upload");
const saveButton = element<HTMLButtonElement>("save");
const preview = new Preview(element<HTMLCanvasElement>("preview"));
const editor = createEditor(element<HTMLDivElement>("editor"), () => schedulePreview());

let previewFrame: number | undefined;

function setStatus(message: string): void {
  status.textContent = message;
}

function schedulePreview(): void {
  if (previewFrame !== undefined) {
    return;
  }
  previewFrame = window.requestAnimationFrame(() => {
    previewFrame = undefined;
    preview.render(editor.getText());
  });
}

async function guard(action: () => Promise<void>): Promise<void> {
  try {
    showError(undefined);
    await action();
  } catch (error) {
    showError(error instanceof Error ? error.message : String(error));
  }
}

async function refreshProjects(): Promise<void> {
  state.projects = await listProjects();
  renderProjectList(projectList, state.projects, (id) => {
    location.hash = `#/projects/${id}`;
  });
}

async function loadFiles(projectId: string): Promise<void> {
  state.files = await listFiles(projectId);
  renderFileList(fileList, state.files, state.currentPath, (path) => {
    void guard(() => openFile(path));
  });
}

async function openFile(path: string): Promise<void> {
  if (!state.project) {
    return;
  }
  const file = await readFile(state.project.id, path);
  state.currentPath = path;
  editor.setText(file.content);
  renderFileList(fileList, state.files, path, (selected) => {
    void guard(() => openFile(selected));
  });
  setStatus("");
  preview.render(editor.getText());
}

async function configureScreen(screenName: string): Promise<void> {
  if (!state.project) {
    return;
  }
  const screen = state.project.manifest.screens.find((item) => item.name === screenName);
  if (!screen) {
    return;
  }
  state.currentScreen = screen.name;
  await preview.configure(
    state.project.id,
    screen,
    state.project.manifest.matches,
    state.project.manifest.tags,
  );
  preview.render(editor.getText());
}

function fillScreens(): void {
  screenSelect.innerHTML = "";
  if (!state.project) {
    return;
  }
  for (const screen of state.project.manifest.screens) {
    const option = document.createElement("option");
    option.value = screen.name;
    option.textContent = screen.name;
    screenSelect.append(option);
  }
}

async function openProject(projectId: string): Promise<void> {
  state.project = await getProject(projectId);
  state.currentPath = undefined;
  fillScreens();
  await loadFiles(projectId);
  const firstScreen = state.project.manifest.screens[0];
  if (firstScreen) {
    await configureScreen(firstScreen.name);
  }
  if (state.files.length > 0) {
    await openFile(state.files[0]);
  } else {
    editor.setText("");
  }
}

async function saveCurrent(): Promise<void> {
  if (!state.project || !state.currentPath) {
    return;
  }
  await saveFile(state.project.id, state.currentPath, editor.getText());
  setStatus("salvo");
}

upload.addEventListener("change", () => {
  const file = upload.files?.[0];
  if (!file) {
    return;
  }
  void guard(async () => {
    const project = await uploadProject(file);
    await refreshProjects();
    location.hash = `#/projects/${project.id}`;
  });
  upload.value = "";
});

saveButton.addEventListener("click", () => {
  void guard(saveCurrent);
});

screenSelect.addEventListener("change", () => {
  void guard(() => configureScreen(screenSelect.value));
});

zoom.addEventListener("input", () => {
  preview.setZoom(Number(zoom.value));
});

window.addEventListener("hashchange", () => {
  const match = /^#\/projects\/(.+)$/.exec(location.hash);
  if (match) {
    void guard(() => openProject(match[1]));
  }
});

preview.setZoom(Number(zoom.value));
void guard(async () => {
  await refreshProjects();
  const match = /^#\/projects\/(.+)$/.exec(location.hash);
  if (match) {
    await openProject(match[1]);
  }
});
