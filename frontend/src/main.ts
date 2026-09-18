import {
  backgroundUrl,
  getAuthMe,
  getProject,
  listFiles,
  listProjects,
  readFile,
  saveFile,
  uploadProject,
} from "./api";
import { createAutosave, type SaveState } from "./autosave";
import { loadAuthConfig, renderLogin } from "./auth";
import { renderAccount } from "./shell/account";
import { createChanges } from "./shell/changes";
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
import { Preview } from "./preview";
import { createCat } from "./shell/cat";
import { createGithubImport } from "./shell/github-import";
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
const appRoot = element<HTMLElement>("app");
const appBar = element<HTMLElement>("app-bar");
const menuSlot = element<HTMLElement>("menu-slot");
const navScrim = element<HTMLElement>("nav-scrim");
const mobileBar = element<HTMLElement>("mobile-editor-bar");
const loginView = element<HTMLElement>("login-view");
const accountSlot = element<HTMLElement>("account-slot");
const changesSlot = element<HTMLElement>("changes-slot");
const sidebar = element<HTMLElement>("docs-sidebar");
const sidebarResizer = element<HTMLElement>("sidebar-resizer");
const previewPane = element<HTMLElement>("preview-pane");
const previewResizer = element<HTMLElement>("preview-resizer");

const SIDEBAR_KEY = "pv-sidebar-width";
const SIDEBAR_MIN = 140;

function sidebarMax(): number {
  return Math.max(320, window.innerWidth * 0.7);
}

function setSidebarWidth(px: number): void {
  const clamped = Math.min(Math.max(px, SIDEBAR_MIN), sidebarMax());
  sidebar.style.setProperty("--pv-sidebar-width", `${clamped}px`);
}

const storedSidebar = (() => {
  try {
    return Number(window.localStorage.getItem(SIDEBAR_KEY)) || 0;
  } catch {
    return 0;
  }
})();
if (storedSidebar > 0) {
  setSidebarWidth(storedSidebar);
}

sidebarResizer.addEventListener("pointerdown", (event) => {
  event.preventDefault();
  sidebarResizer.setPointerCapture(event.pointerId);
  sidebarResizer.classList.add("active");
  const startX = event.clientX;
  const startWidth = sidebar.getBoundingClientRect().width;
  const onMove = (move: PointerEvent): void => {
    setSidebarWidth(startWidth + (move.clientX - startX));
  };
  const onUp = (): void => {
    sidebarResizer.classList.remove("active");
    sidebarResizer.removeEventListener("pointermove", onMove);
    sidebarResizer.removeEventListener("pointerup", onUp);
    try {
      window.localStorage.setItem(
        SIDEBAR_KEY,
        String(Math.round(sidebar.getBoundingClientRect().width)),
      );
    } catch {
      // armazenamento indisponível: ignora
    }
  };
  sidebarResizer.addEventListener("pointermove", onMove);
  sidebarResizer.addEventListener("pointerup", onUp);
});

sidebarResizer.addEventListener("dblclick", () => {
  sidebar.style.removeProperty("--pv-sidebar-width");
  try {
    window.localStorage.removeItem(SIDEBAR_KEY);
  } catch {
    // armazenamento indisponível: ignora
  }
});

const PREVIEW_KEY = "pv-preview-width";

function previewMax(): number {
  return Math.max(320, window.innerWidth * 0.8);
}

function setPreviewWidth(px: number): void {
  const clamped = Math.min(Math.max(px, previewMin()), previewMax());
  previewPane.style.setProperty("--pv-preview-width", `${clamped}px`);
}

previewResizer.addEventListener("pointerdown", (event) => {
  event.preventDefault();
  previewResizer.setPointerCapture(event.pointerId);
  previewResizer.classList.add("active");
  const startX = event.clientX;
  const startWidth = previewPane.getBoundingClientRect().width;
  const onMove = (move: PointerEvent): void => {
    setPreviewWidth(startWidth - (move.clientX - startX));
  };
  const onUp = (): void => {
    previewResizer.classList.remove("active");
    previewResizer.removeEventListener("pointermove", onMove);
    previewResizer.removeEventListener("pointerup", onUp);
    try {
      window.localStorage.setItem(
        PREVIEW_KEY,
        String(Math.round(previewPane.getBoundingClientRect().width)),
      );
    } catch {
      // armazenamento indisponível: ignora
    }
  };
  previewResizer.addEventListener("pointermove", onMove);
  previewResizer.addEventListener("pointerup", onUp);
});

previewResizer.addEventListener("dblclick", () => {
  previewPane.style.removeProperty("--pv-preview-width");
  try {
    window.localStorage.removeItem(PREVIEW_KEY);
  } catch {
    // armazenamento indisponível: ignora
  }
});
const projectSlot = element<HTMLDivElement>("project-slot");
const viewSlot = element<HTMLDivElement>("view-slot");
const saveSlot = element<HTMLDivElement>("save-slot");
const navSlot = element<HTMLDivElement>("nav-slot");
const themeSlot = element<HTMLDivElement>("theme-slot");
const screenSlot = element<HTMLDivElement>("screen-slot");
const errorSlot = element<HTMLDivElement>("error-slot");
const tabsContainer = element<HTMLDivElement>("tabs");
const originalPane = element<HTMLElement>("original-pane");
const editorHost = element<HTMLElement>("editor");
const catHost = element<HTMLElement>("cat-host");
const previewStage = element<HTMLElement>("preview-stage");
const upload = element<HTMLInputElement>("upload");
const previewCanvas = element<HTMLCanvasElement>("preview");
const preview = new Preview(previewCanvas);

function previewMin(): number {
  const body = previewStage.parentElement;
  if (!body) {
    return previewCanvas.width;
  }
  const style = window.getComputedStyle(body);
  const padding = parseFloat(style.paddingLeft) + parseFloat(style.paddingRight);
  return previewCanvas.width + padding;
}

function fitPreview(): void {
  const width = previewStage.clientWidth;
  const height = previewStage.clientHeight;
  if (width <= 0 || height <= 0) {
    return;
  }
  const scale = Math.max(
    1,
    Math.min(
      Math.floor(width / previewCanvas.width),
      Math.floor(height / previewCanvas.height),
    ),
  );
  preview.setZoom(scale);
  previewPane.style.setProperty(
    "--pv-preview-image-width",
    `${previewCanvas.width}px`,
  );
}

new ResizeObserver(() => fitPreview()).observe(previewStage);

const storedPreview = (() => {
  try {
    return Number(window.localStorage.getItem(PREVIEW_KEY)) || 0;
  } catch {
    return 0;
  }
})();
if (storedPreview > 0) {
  setPreviewWidth(storedPreview);
}

const editor = createEditor(editorHost, () => onEditorChange());
const originalEditor = createReadOnlyEditor(element<HTMLDivElement>("original"));
const cat = createCat({
  onTranslatedChange: onCatChange,
  onSelect: onCatSelect,
  onOpen: (index) => {
    focusMobileSegment(index);
  },
});
catHost.append(cat.element);

const mobileQuery = window.matchMedia("(max-width: 640px)");

const menuButton = document.createElement("button");
menuButton.type = "button";
menuButton.className = "pv-icon-btn";
menuButton.title = "Menu";
menuButton.setAttribute("aria-label", "Menu");
menuButton.append(kit.icon("bars", "Menu"));
menuButton.addEventListener("click", () => {
  setNav(!document.documentElement.classList.contains("nav-open"));
});
menuSlot.append(menuButton);

function setNav(open: boolean): void {
  document.documentElement.classList.toggle("nav-open", open);
  navScrim.hidden = !open;
}

navScrim.addEventListener("click", () => setNav(false));

function focusMobileSegment(index: number): void {
  if (cat.count() === 0) {
    return;
  }
  const clamped = Math.max(0, Math.min(cat.count() - 1, index));
  cat.focus(clamped);
  mobileBar.hidden = false;
}

function applyMobileLayout(): void {
  const mobile = mobileQuery.matches;
  document.documentElement.classList.toggle("pv-mobile", mobile);
  if (mobile) {
    if (projectSlot.parentElement !== sidebar) {
      sidebar.prepend(projectSlot);
    }
  } else if (projectSlot.parentElement !== appBar) {
    appBar.insertBefore(projectSlot, viewSlot);
  }
  setNav(false);
  if (mobile) {
    setView("cat");
    mobileBar.hidden = true;
  }
}

function setupMobileBar(): void {
  mobileBar.querySelector('[data-action="prev"]')?.addEventListener("click", () => {
    focusMobileSegment(cat.activeIndex() - 1);
  });
  mobileBar.querySelector('[data-action="next"]')?.addEventListener("click", () => {
    focusMobileSegment(cat.activeIndex() + 1);
  });
  mobileBar.querySelector('[data-action="list"]')?.addEventListener("click", () => {
    cat.showList();
    mobileBar.hidden = true;
  });
}

setupMobileBar();
mobileQuery.addEventListener("change", applyMobileLayout);

let previewFrame: number | undefined;
let previewCursor = 0;
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

const githubImport = createGithubImport({
  onImported: (projectId) => {
    void guard(async () => {
      await refreshProjects();
      location.hash = `#/projects/${projectId}`;
    });
  },
});
document.body.append(githubImport.element);

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

const saveIndicator = document.createElement("span");
saveIndicator.className = "pv-save";
saveIndicator.hidden = true;

const saveButton = document.createElement("button");
saveButton.type = "button";
saveButton.className = "pv-head-btn";
saveButton.textContent = "Salvar";
saveButton.addEventListener("click", () => {
  if (saveButton.disabled) {
    return;
  }
  void guard(async () => {
    saveButton.disabled = true;
    saveButton.textContent = "Salvando…";
    try {
      await autosave.flush();
      await changesHandle.backup();
    } finally {
      saveButton.disabled = false;
      saveButton.textContent = "Salvar";
    }
  });
});

saveSlot.append(saveIndicator, saveButton);

let savedFlash: ReturnType<typeof setTimeout> | undefined;

function renderSaveState(value: SaveState): void {
  if (savedFlash !== undefined) {
    clearTimeout(savedFlash);
    savedFlash = undefined;
  }
  saveIndicator.className = `pv-save pv-save--${value}`;
  saveIndicator.replaceChildren();
  if (value === "idle") {
    saveIndicator.hidden = true;
    return;
  }
  if (value === "saved") {
    saveIndicator.textContent = "✓";
    saveIndicator.hidden = false;
    savedFlash = setTimeout(() => {
      savedFlash = undefined;
      saveIndicator.hidden = true;
    }, 1500);
    return;
  }
  if (value === "offline") {
    saveIndicator.append(kit.icon("ban", "Erro ao salvar"));
    saveIndicator.hidden = false;
    return;
  }
  saveIndicator.hidden = true;
}

let suppressSave = false;

const autosave = createAutosave({
  save: () => persistActiveDocument(),
  onState: renderSaveState,
});

const busyOverlay = document.createElement("div");
busyOverlay.className = "pv-busy";
busyOverlay.hidden = true;
const busyBox = document.createElement("div");
busyBox.className = "pv-busy-box";
const busySpinner = document.createElement("div");
busySpinner.className = "pv-busy-spinner";
const busyLabel = document.createElement("span");
busyLabel.textContent = "Carregando…";
busyBox.append(busySpinner, busyLabel);
busyOverlay.append(busyBox);
document.body.append(busyOverlay);

let busyCount = 0;
let busyTimer: number | undefined;

function setBusy(busy: boolean, label = "Carregando…"): void {
  if (busy) {
    busyCount += 1;
    busyLabel.textContent = label;
    if (busyCount === 1) {
      busyTimer = window.setTimeout(() => {
        busyTimer = undefined;
        busyOverlay.hidden = false;
      }, 150);
    }
  } else {
    busyCount = Math.max(0, busyCount - 1);
    if (busyCount === 0) {
      if (busyTimer !== undefined) {
        window.clearTimeout(busyTimer);
        busyTimer = undefined;
      }
      busyOverlay.hidden = true;
    }
  }
}

const changesHandle = createChanges({
  onReload: () => reloadWorkspace(),
  onBusy: (busy, label) => setBusy(busy, label),
});
changesSlot.append(changesHandle.element);

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

function schedulePreview(cursorLine = 0): void {
  previewCursor = cursorLine;
  if (previewFrame !== undefined) {
    return;
  }
  previewFrame = window.requestAnimationFrame(() => {
    previewFrame = undefined;
    preview.render(editor.getText(), previewCursor);
  });
}

async function guard(action: () => Promise<void>): Promise<void> {
  try {
    showError(undefined);
    setBusy(true);
    await action();
  } catch (error) {
    showError(error instanceof Error ? error.message : String(error));
  } finally {
    setBusy(false);
  }
}

function activeDoc(): OpenDocument | undefined {
  return state.activePath ? findDocument(state.documents, state.activePath) : undefined;
}

function loadCat(doc: OpenDocument | undefined, fallbackContent = ""): void {
  const segments = state.project?.manifest.segments;
  cat.setBrowse(mobileQuery.matches);
  mobileBar.hidden = true;
  cat.load(
    doc?.content ?? fallbackContent,
    doc?.original ?? null,
    segments?.start ?? [],
    segments?.end ?? [],
    segments?.separators ?? [],
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
  originalPane.hidden = catMode;
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
  autosave.schedule();
}

function onCatChange(text: string): void {
  if (!state.activePath) {
    return;
  }
  state.documents = markModified(state.documents, state.activePath, text);
  editor.setText(text);
  updateModifiedIndicator();
  refreshTabs();
  schedulePreview(cat.activeStartLine() ?? 0);
  autosave.schedule();
}

function onCatSelect(startLine: number): void {
  preview.render(editor.getText(), startLine);
}

function updateModifiedIndicator(): void {
  const doc = activeDoc();
  if (!doc?.modified) {
    renderSaveState("idle");
  }
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
  const githubItem = document.createElement("button");
  githubItem.type = "button";
  githubItem.textContent = "Importar do GitHub…";
  githubItem.addEventListener("click", () => {
    projectMenu.hidden = true;
    githubImport.open();
  });
  projectMenu.append(githubItem);
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
    (path) => void closeDocumentTab(path),
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
  screenButton.className = "pv-head-btn";
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
  if (!suppressSave && state.activePath && state.activePath !== path) {
    const previous = findDocument(state.documents, state.activePath);
    if (previous?.modified) {
      await autosave.flush();
    }
  }
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

async function closeDocumentTab(path: string): Promise<void> {
  if (!suppressSave && state.activePath === path) {
    const doc = findDocument(state.documents, path);
    if (doc?.modified) {
      await autosave.flush();
    }
  }
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
  if (state.project && !suppressSave) {
    const doc = activeDoc();
    if (doc?.modified) {
      await autosave.flush();
    }
  }
  state.project = await getProject(projectId);
  state.activePath = undefined;
  state.documents = [];
  renderProjectSelector();
  renderScreenSelector();
  changesHandle.setProject(projectId);
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
  await changesHandle.refresh();
}

async function persistActiveDocument(): Promise<void> {
  if (suppressSave) {
    return;
  }
  const doc = activeDoc();
  if (!state.project || !doc || !doc.modified) {
    return;
  }
  const text = editor.getText();
  await saveFile(state.project.id, doc.path, text);
  state.documents = markSaved(state.documents, doc.path, text);
  updateModifiedIndicator();
  refreshTabs();
  await changesHandle.refresh();
}

async function reloadWorkspace(): Promise<void> {
  if (!state.project) {
    return;
  }
  const projectId = state.project.id;
  suppressSave = true;
  try {
    state.project = await getProject(projectId);
    renderProjectSelector();
    renderScreenSelector();
    const screen =
      state.project.manifest.screens.find(
        (item) => item.name === state.currentScreen,
      ) ?? state.project.manifest.screens[0];
    if (screen) {
      await configureScreen(screen.name);
    }
    await loadFiles(projectId);
    const path = state.activePath;
    if (path && state.files.includes(path)) {
      state.documents = closeDocument(state.documents, path);
      await openDocument(path);
    } else if (state.files.length > 0) {
      await openDocument(state.files[0]);
    } else {
      clearActiveDocument();
    }
  } finally {
    suppressSave = false;
  }
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

window.addEventListener("pagehide", () => {
  void changesHandle.backup(true);
});

window.addEventListener("hashchange", () => {
  const match = /^#\/projects\/(.+)$/.exec(location.hash);
  if (match) {
    void guard(() => openProject(match[1]));
  }
});

// --- Inicialização ----------------------------------------------------------
applyTheme();
renderProjectSelector();
renderScreenSelector();
renderSaveState("idle");
setView("editor");
applyMobileLayout();
fitPreview();

const AUTH_MESSAGES: Record<string, string> = {
  denied: "Acesso negado: sua conta não está autorizada.",
  invalid_state: "A sessão de login expirou. Tente novamente.",
  error: "Não foi possível concluir o login. Tente novamente.",
};

void (async () => {
  try {
    const [config, me] = await Promise.all([loadAuthConfig(), getAuthMe()]);
    state.authConfig = config;
    if (!me.authenticated || !me.user) {
      const authError = new URLSearchParams(window.location.search).get("auth");
      appRoot.hidden = true;
      renderLogin(loginView, config, authError ? AUTH_MESSAGES[authError] : undefined);
      return;
    }
    state.auth = me.user;
    appRoot.hidden = false;
    renderAccount(accountSlot, me.user, config);
    await guard(async () => {
      await refreshProjects();
      const match = /^#\/projects\/(.+)$/.exec(location.hash);
      if (match) {
        await openProject(match[1]);
      }
    });
  } catch (error) {
    showError(error instanceof Error ? error.message : String(error));
  }
})();
