import {
  backgroundUrl,
  getProject,
  listFiles,
  listProjects,
  readFile,
  saveFile,
  uploadProject,
} from "./api";
import {
  addDocument,
  closeDocument,
  findDocument,
  markModified,
  markSaved,
  pathAfterClose,
  updateContent,
  type OpenDocument,
} from "./documents";
import { createEditor, createReadOnlyEditor } from "./editor";
import { Preview, SCREEN_HEIGHT, SCREEN_WIDTH } from "./preview";
import { createCat } from "./shell/cat";
import { renderTabs } from "./shell/tabs";
import { renderFileTree } from "./shell/tree";
import { kit, type Theme } from "./ui";
import { state } from "./state";

import "./ui/tokens.css";
import "./ui/theme-webawesome.css";
import "./ui/layout.css";

type ViewMode = "editor" | "cat";

function element<T extends HTMLElement>(id: string): T {
  const found = document.getElementById(id);
  if (!found) {
    throw new Error(`elemento ausente: ${id}`);
  }
  return found as T;
}

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

const fileList = element<HTMLElement>("file-list");
const projectSlot = element<HTMLDivElement>("project-slot");
const viewSlot = element<HTMLDivElement>("view-slot");
const textActionsSlot = element<HTMLDivElement>("text-actions-slot");
const navSlot = element<HTMLDivElement>("nav-slot");
const themeSlot = element<HTMLDivElement>("theme-slot");
const screenSlot = element<HTMLDivElement>("screen-slot");
const errorSlot = element<HTMLDivElement>("error-slot");
const tabsContainer = element<HTMLDivElement>("tabs");
const originalPane = element<HTMLElement>("original-pane");
const editorHost = element<HTMLElement>("editor");
const catHost = element<HTMLElement>("cat-host");
const zoom = element<HTMLInputElement>("zoom");
const previewStage = element<HTMLDivElement>("preview-stage");
const upload = element<HTMLInputElement>("upload");
const preview = new Preview(element<HTMLCanvasElement>("preview"));
const editor = createEditor(editorHost, () => onEditorChange());
const originalEditor = createReadOnlyEditor(element<HTMLDivElement>("original"));
const cat = createCat({ onTranslatedChange: onCatChange, onSelect: onCatSelect });
catHost.append(cat.element);

let previewFrame: number | undefined;
let view: ViewMode = "editor";

const errorCallout = kit.callout("", "danger");
errorSlot.append(errorCallout.element);

// --- Barra de comando -------------------------------------------------------
const projectButton = document.createElement("button");
projectButton.type = "button";
projectButton.className = "pv-btn";
const projectMenu = document.createElement("div");
projectMenu.className = "pv-menu";
projectMenu.hidden = true;
projectSlot.append(projectButton, projectMenu);

projectButton.addEventListener("click", () => {
  projectMenu.hidden = !projectMenu.hidden;
});
document.addEventListener("click", (event) => {
  if (!projectSlot.contains(event.target as Node)) {
    projectMenu.hidden = true;
  }
});

screenSlot.classList.add("pv-project");
const screenButton = document.createElement("button");
screenButton.type = "button";
screenButton.className = "pv-btn";
screenSlot.append(screenButton);
screenButton.addEventListener("click", () => openScreenModal());

const screenModal = document.createElement("div");
screenModal.className = "pv-modal";
screenModal.hidden = true;
const screenDialog = document.createElement("div");
screenDialog.className = "pv-modal-dialog";
screenDialog.setAttribute("role", "dialog");
screenDialog.setAttribute("aria-modal", "true");
screenDialog.setAttribute("aria-label", "Escolher tela");
screenModal.append(screenDialog);

const modalHead = document.createElement("div");
modalHead.className = "pv-modal-head";
const modalTitle = document.createElement("h2");
modalTitle.textContent = "Escolher tela";
const modalClose = iconButton("xmark", "Fechar", () => closeScreenModal());
modalHead.append(modalTitle, modalClose);

const modalSplit = document.createElement("div");
modalSplit.className = "pv-modal-split";
const modalPreview = document.createElement("div");
modalPreview.className = "pv-screen-preview";
const previewImage = document.createElement("img");
previewImage.className = "pv-screen-image";
previewImage.alt = "";
const previewCaption = document.createElement("div");
previewCaption.className = "pv-screen-caption";
modalPreview.append(previewImage, previewCaption);
const modalList = document.createElement("div");
modalList.className = "pv-screen-list";
modalSplit.append(modalPreview, modalList);

const modalFoot = document.createElement("div");
modalFoot.className = "pv-modal-foot";
const cancelButton = document.createElement("button");
cancelButton.type = "button";
cancelButton.className = "pv-btn";
cancelButton.textContent = "Cancelar";
cancelButton.addEventListener("click", () => closeScreenModal());
const applyButton = document.createElement("button");
applyButton.type = "button";
applyButton.className = "pv-btn pv-btn--primary";
applyButton.textContent = "Aplicar";
applyButton.addEventListener("click", () => {
  const name = pendingScreen;
  closeScreenModal();
  if (name) {
    void guard(() => configureScreen(name));
  }
});
modalFoot.append(cancelButton, applyButton);

screenDialog.append(modalHead, modalSplit, modalFoot);
screenModal.addEventListener("mousedown", (event) => {
  if (event.target === screenModal) {
    closeScreenModal();
  }
});
document.body.append(screenModal);

let pendingScreen: string | undefined;

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !screenModal.hidden) {
    closeScreenModal();
  }
});

const segmentsButton = document.createElement("button");
segmentsButton.type = "button";
segmentsButton.className = "pv-seg";
segmentsButton.textContent = "Segmentos";
segmentsButton.addEventListener("click", () => setView("cat"));

const editorButton = document.createElement("button");
editorButton.type = "button";
editorButton.className = "pv-seg";
editorButton.textContent = "Editor";
editorButton.addEventListener("click", () => setView("editor"));

viewSlot.append(segmentsButton, editorButton);

const saveButton = document.createElement("button");
saveButton.type = "button";
saveButton.className = "pv-btn pv-btn--primary";
saveButton.textContent = "Salvar";
saveButton.addEventListener("click", () => {
  void guard(saveCurrent);
});

const originalButton = document.createElement("button");
originalButton.type = "button";
originalButton.className = "pv-btn";
originalButton.textContent = "Original";
originalButton.addEventListener("click", toggleOriginal);

const dirtyIndicator = document.createElement("span");
dirtyIndicator.className = "pv-dirty";
dirtyIndicator.hidden = true;
dirtyIndicator.title = "não salvo";

textActionsSlot.append(saveButton, originalButton, dirtyIndicator);

navSlot.append(
  iconButton("chevron-up", "Segmento anterior", () => cat.move(-1)),
  iconButton("chevron-down", "Próximo segmento", () => cat.move(1)),
);

const THEMES: Theme[] = ["system", "light", "dark"];
const THEME_ICON: Record<Theme, string> = {
  system: "circle-half-stroke",
  light: "sun",
  dark: "moon",
};
const stored = (() => {
  try {
    return window.localStorage.getItem("pv-theme") as Theme | null;
  } catch {
    return null;
  }
})();
let themeIndex = stored && THEMES.includes(stored) ? THEMES.indexOf(stored) : 0;

const themeButton = iconButton("circle-half-stroke", "Tema", () => {
  themeIndex = (themeIndex + 1) % THEMES.length;
  applyTheme();
});
themeSlot.append(themeButton);

// --- Estado/seleções --------------------------------------------------------
function showError(message?: string): void {
  if (message) {
    errorCallout.setMessage(message);
    errorCallout.element.hidden = false;
    errorSlot.hidden = false;
  } else {
    errorCallout.element.hidden = true;
    errorSlot.hidden = true;
  }
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

function activeDoc(): OpenDocument | undefined {
  return state.activePath ? findDocument(state.documents, state.activePath) : undefined;
}

function loadCat(doc: OpenDocument | undefined, fallbackContent = ""): void {
  const segments = state.project?.manifest.segments;
  cat.load(
    doc?.content ?? fallbackContent,
    doc?.original ?? null,
    segments?.start ?? [],
    segments?.end ?? [],
  );
}

function updateViewButtons(): void {
  segmentsButton.classList.toggle("active", view === "cat");
  editorButton.classList.toggle("active", view === "editor");
  navSlot.hidden = view !== "cat";
}

function setView(next: ViewMode): void {
  view = next;
  const catMode = next === "cat";
  editorHost.hidden = catMode;
  catHost.hidden = !catMode;
  originalPane.hidden = catMode || !state.showOriginal;
  updateViewButtons();
  if (catMode) {
    loadCat(activeDoc());
  } else {
    const doc = activeDoc();
    if (doc) {
      editor.setText(doc.content);
    }
    editor.requestMeasure();
    preview.render(editor.getText());
  }
}

function onEditorChange(): void {
  if (!state.activePath) {
    return;
  }
  state.documents = markModified(state.documents, state.activePath, editor.getText());
  updateModifiedIndicator();
  refreshTabs();
  schedulePreview();
}

function onCatChange(text: string): void {
  if (!state.activePath) {
    return;
  }
  state.documents = markModified(state.documents, state.activePath, text);
  editor.setText(text);
  updateModifiedIndicator();
  refreshTabs();
  schedulePreview();
}

function onCatSelect(startLine: number): void {
  preview.render(editor.getText(), startLine);
}

function updateModifiedIndicator(): void {
  const doc = activeDoc();
  dirtyIndicator.hidden = !doc?.modified;
}

function renderProjectSelector(): void {
  projectButton.replaceChildren();
  const name = document.createElement("span");
  name.textContent = state.project?.name ?? "nenhum projeto";
  const caret = document.createElement("span");
  caret.className = "pv-caret";
  caret.textContent = "▾";
  projectButton.append(name, caret);

  projectMenu.replaceChildren();
  for (const project of state.projects) {
    const item = document.createElement("button");
    item.type = "button";
    item.textContent = project.name;
    item.classList.toggle("active", project.id === state.project?.id);
    item.addEventListener("click", () => {
      projectMenu.hidden = true;
      location.hash = `#/projects/${project.id}`;
    });
    projectMenu.append(item);
  }
  const importItem = document.createElement("button");
  importItem.type = "button";
  importItem.textContent = "Importar .zip…";
  importItem.addEventListener("click", () => {
    projectMenu.hidden = true;
    upload.click();
  });
  projectMenu.append(importItem);
  if (state.project) {
    const meta = document.createElement("div");
    meta.className = "meta";
    const segmented = state.project.manifest.segments ? " · segmentado" : "";
    meta.textContent = `${state.project.encoding}${segmented}`;
    projectMenu.append(meta);
  }
}

function refreshTabs(): void {
  renderTabs(
    tabsContainer,
    state.documents,
    state.activePath,
    (path) => void guard(() => activateDocument(path)),
    (path) => closeDocumentTab(path),
  );
}

function refreshFileList(): void {
  const prefix = state.project
    ? `${state.project.manifest.texts.source.replace(/\/+$/, "")}/`
    : "";
  renderFileTree(fileList, state.files, prefix, state.activePath, (path) => {
    void guard(() => openDocument(path));
  });
}

async function refreshProjects(): Promise<void> {
  state.projects = await listProjects();
  renderProjectSelector();
}

function renderScreenSelector(): void {
  screenButton.replaceChildren();
  const icon = kit.icon("table-cells-large", "telas");
  icon.classList.add("pv-screen-btn-icon");
  const label = document.createElement("span");
  label.textContent = "Tela";
  screenButton.append(icon, label);
}

function renderScreenList(): void {
  modalList.replaceChildren();
  if (!state.project) {
    return;
  }
  for (const screen of state.project.manifest.screens) {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "pv-screen-item";
    item.classList.toggle("active", screen.name === pendingScreen);

    const background = state.project.manifest.backgrounds.find(
      (asset) => asset.name === screen.background,
    );
    if (background) {
      const mini = document.createElement("img");
      mini.className = "pv-screen-mini";
      mini.alt = "";
      mini.src = backgroundUrl(state.project.id, background.name);
      item.append(mini);
    }

    const label = document.createElement("span");
    label.textContent = screen.name;
    item.append(label);

    item.addEventListener("click", () => {
      pendingScreen = screen.name;
      renderScreenList();
      renderScreenPreview();
    });
    modalList.append(item);
  }
}

function renderScreenPreview(): void {
  if (!state.project || !pendingScreen) {
    return;
  }
  const screen = state.project.manifest.screens.find((item) => item.name === pendingScreen);
  if (!screen) {
    return;
  }
  const background = state.project.manifest.backgrounds.find(
    (asset) => asset.name === screen.background,
  );
  previewImage.src = background ? backgroundUrl(state.project.id, background.name) : "";
  previewCaption.textContent = `${screen.name} · ${screen.font} · x ${screen.x} · y ${screen.y} · linha ${screen.new_line}`;
}

function openScreenModal(): void {
  if (!state.project) {
    return;
  }
  const screens = state.project.manifest.screens;
  if (screens.length === 0) {
    return;
  }
  pendingScreen =
    screens.find((screen) => screen.name === state.currentScreen)?.name ?? screens[0].name;
  renderScreenList();
  renderScreenPreview();
  screenModal.hidden = false;
}

function closeScreenModal(): void {
  screenModal.hidden = true;
}

async function activateDocument(path: string): Promise<void> {
  if (state.activePath && state.activePath !== path) {
    state.documents = updateContent(state.documents, state.activePath, editor.getText());
  }
  const doc = findDocument(state.documents, path);
  if (!doc) {
    return;
  }
  state.activePath = path;
  editor.setText(doc.content);
  originalEditor.setText(doc.original ?? "(sem texto original)");
  if (view === "cat") {
    loadCat(doc);
  }
  updateModifiedIndicator();
  refreshTabs();
  refreshFileList();
  preview.render(editor.getText());
}

async function openDocument(path: string): Promise<void> {
  if (!state.project) {
    return;
  }
  if (findDocument(state.documents, path)) {
    await activateDocument(path);
    return;
  }
  const [file, original] = await Promise.all([
    readFile(state.project.id, path),
    readFile(state.project.id, path, "original").catch(() => null),
  ]);
  state.documents = addDocument(state.documents, {
    path,
    content: file.content,
    original: original ? original.content : null,
    modified: false,
  });
  await activateDocument(path);
}

function clearActiveDocument(): void {
  state.activePath = undefined;
  editor.setText("");
  originalEditor.setText("");
  if (view === "cat") {
    loadCat(undefined);
  }
  updateModifiedIndicator();
  refreshTabs();
  refreshFileList();
}

function closeDocumentTab(path: string): void {
  const next = pathAfterClose(state.documents, path);
  state.documents = closeDocument(state.documents, path);
  if (state.activePath !== path) {
    refreshTabs();
    return;
  }
  if (next) {
    void guard(() => activateDocument(next));
  } else {
    clearActiveDocument();
  }
}

async function loadFiles(projectId: string): Promise<void> {
  state.files = await listFiles(projectId);
  refreshFileList();
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
  renderScreenSelector();
}

async function openProject(projectId: string): Promise<void> {
  state.project = await getProject(projectId);
  state.activePath = undefined;
  state.documents = [];
  renderProjectSelector();
  renderScreenSelector();
  await loadFiles(projectId);
  clearActiveDocument();
  const firstScreen = state.project.manifest.screens[0];
  if (firstScreen) {
    await configureScreen(firstScreen.name);
  }
  if (state.files.length > 0) {
    await openDocument(state.files[0]);
  }
  setView(state.project.manifest.segments ? "cat" : "editor");
}

async function saveCurrent(): Promise<void> {
  const doc = activeDoc();
  if (!state.project || !doc) {
    return;
  }
  await saveFile(state.project.id, doc.path, editor.getText());
  state.documents = markSaved(state.documents, doc.path, editor.getText());
  updateModifiedIndicator();
  refreshTabs();
  kit.toast({ message: "Arquivo salvo", variant: "success" });
}

function toggleOriginal(): void {
  state.showOriginal = !state.showOriginal;
  originalPane.hidden = view === "cat" || !state.showOriginal;
  originalButton.classList.toggle("active", state.showOriginal);
}

function applyTheme(): void {
  const theme = THEMES[themeIndex];
  kit.applyTheme(theme);
  themeButton.replaceChildren(kit.icon(THEME_ICON[theme], "tema"));
}

// --- Eventos ----------------------------------------------------------------
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

function applyZoom(): void {
  const value = Number(zoom.value);
  previewStage.style.width = `${SCREEN_WIDTH * value}px`;
  previewStage.style.height = `${SCREEN_HEIGHT * value}px`;
}

zoom.addEventListener("input", applyZoom);

window.addEventListener("hashchange", () => {
  const match = /^#\/projects\/(.+)$/.exec(location.hash);
  if (match) {
    void guard(() => openProject(match[1]));
  }
});

// --- Inicialização ----------------------------------------------------------
originalButton.classList.toggle("active", state.showOriginal);
applyTheme();
renderProjectSelector();
renderScreenSelector();
setView("editor");
originalPane.hidden = !state.showOriginal;
applyZoom();

void guard(async () => {
  await refreshProjects();
  const match = /^#\/projects\/(.+)$/.exec(location.hash);
  if (match) {
    await openProject(match[1]);
  }
});
