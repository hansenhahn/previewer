import {
  abandonChange,
  backupChange,
  discardChange,
  getChangeState,
  listChanges,
  newChange,
  publishChange,
  resumeChange,
  type ChangeInfo,
  type ChangeState,
} from "../api";
import { kit } from "../ui";

export interface ChangesOptions {
  onReload: () => Promise<void>;
  onBusy?: (busy: boolean, label?: string) => void;
}

export interface ChangesHandle {
  element: HTMLElement;
  setProject(projectId: string | undefined): void;
  refresh(): Promise<void>;
  backup(keepalive?: boolean): Promise<void>;
}

function stem(change: ChangeInfo): string {
  if (change.title) {
    return change.title;
  }
  return change.branch
    .replace(/^previewer\//, "")
    .replace(/-/g, " ")
    .trim();
}

function chipLabel(change: ChangeInfo): string {
  switch (change.status) {
    case "draft":
      return "rascunho";
    case "changes_requested":
      return `PR #${change.pr_number} · revisão`;
    case "merged":
      return `PR #${change.pr_number} · mergeada`;
    case "closed":
      return `PR #${change.pr_number} · fechada`;
    default:
      return `PR #${change.pr_number}`;
  }
}

function statusText(change: ChangeInfo): string {
  switch (change.status) {
    case "draft":
      return "rascunho · não enviado";
    case "changes_requested":
      return `PR #${change.pr_number} · mudanças solicitadas`;
    case "merged":
      return `PR #${change.pr_number} · mergeada`;
    case "closed":
      return `PR #${change.pr_number} · fechada`;
    default:
      return `PR #${change.pr_number} · aberto`;
  }
}

function chipVariant(status: ChangeState["status"]): string {
  switch (status) {
    case "draft":
      return "draft";
    case "open":
      return "open";
    case "changes_requested":
      return "requested";
    case "merged":
      return "merged";
    case "closed":
      return "closed";
    default:
      return "base";
  }
}

export function createChanges(options: ChangesOptions): ChangesHandle {
  let projectId: string | undefined;
  let current: ChangeState | null = null;
  let changes: ChangeInfo[] = [];

  const busy = (value: boolean, label?: string): void =>
    options.onBusy?.(value, label);

  const element = document.createElement("div");
  element.className = "pv-chipwrap";

  const chip = document.createElement("button");
  chip.type = "button";
  chip.className = "pv-chip pv-chip--base";
  chip.setAttribute("aria-haspopup", "menu");

  const menu = document.createElement("div");
  menu.className = "pv-chip-menu";
  menu.hidden = true;

  const publishItem = menuItem("arrow-up", "Subir rascunho", () => void openPublish());
  const newItem = menuItem("plus", "Novo rascunho", () => void openNew());
  const resumeItem = menuItem("arrows-rotate", "Retomar rascunho…", () => void openResume());
  const discardItem = menuItem("trash", "Descartar rascunho", () => void openDiscard());

  menu.append(
    publishItem.element,
    newItem.element,
    resumeItem.element,
    discardItem.element,
  );
  element.append(chip, menu);

  chip.addEventListener("click", () => {
    menu.hidden = !menu.hidden;
  });
  document.addEventListener("click", (event) => {
    if (!element.contains(event.target as Node)) {
      menu.hidden = true;
    }
  });

  function menuItem(icon: string, label: string, onSelect: () => void) {
    const item = document.createElement("button");
    item.type = "button";
    const glyph = kit.icon(icon);
    const text = document.createElement("span");
    text.textContent = label;
    item.append(glyph, text);
    item.addEventListener("click", () => {
      if (item.disabled) {
        return;
      }
      menu.hidden = true;
      onSelect();
    });
    return { element: item, setDisabled: (value: boolean) => (item.disabled = value) };
  }

  function render(): void {
    const status = current?.status ?? "base";
    chip.className = `pv-chip pv-chip--${chipVariant(status)}`;
    chip.replaceChildren();
    const label = document.createElement("span");
    label.textContent =
      current?.change && status !== "base" ? chipLabel(current.change) : "sem alteração";
    const caret = document.createElement("span");
    caret.className = "pv-caret";
    caret.textContent = "▾";
    chip.append(label, caret);

    const hasChange = Boolean(current?.change);
    publishItem.setDisabled(!(current?.can_publish && hasChange));
    newItem.setDisabled(!hasChange || current?.status === "draft");
    resumeItem.setDisabled(changes.length === 0);
    discardItem.setDisabled(!hasChange);
  }

  async function openNew(): Promise<void> {
    if (!projectId) {
      return;
    }
    busy(true, "Preparando novo rascunho…");
    try {
      await newChange(projectId);
      await refresh();
      await options.onReload();
    } catch (error) {
      kit.toast({
        message: error instanceof Error ? error.message : String(error),
        variant: "danger",
      });
    } finally {
      busy(false);
    }
  }

  async function backup(keepalive = false): Promise<void> {
    const change = current?.change;
    if (!projectId || !change || change.pr_number != null) {
      return;
    }
    await backupChange(projectId, change.id, keepalive);
  }

  function modal(title: string, ariaLabel: string): {
    body: HTMLElement;
    footer: HTMLElement;
    close: () => void;
  } {
    const overlay = document.createElement("div");
    overlay.className = "pv-modal";
    const dialog = document.createElement("div");
    dialog.className = "pv-modal-dialog pv-dialog";
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("aria-label", ariaLabel);

    const head = document.createElement("div");
    head.className = "pv-modal-head";
    const heading = document.createElement("h2");
    heading.textContent = title;
    const closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className = "pv-icon-btn";
    closeButton.setAttribute("aria-label", "Fechar");
    closeButton.append(kit.icon("xmark", "Fechar"));
    head.append(heading, closeButton);

    const body = document.createElement("div");
    body.className = "pv-dialog-body";
    const footer = document.createElement("div");
    footer.className = "pv-modal-foot";
    dialog.append(head, body, footer);
    overlay.append(dialog);

    const close = (): void => {
      overlay.remove();
    };
    closeButton.addEventListener("click", close);
    overlay.addEventListener("mousedown", (event) => {
      if (event.target === overlay) {
        close();
      }
    });
    document.addEventListener("keydown", function onKey(event) {
      if (event.key === "Escape") {
        document.removeEventListener("keydown", onKey);
        close();
      }
    });
    document.body.append(overlay);
    return { body, footer, close };
  }

  function button(label: string, variant: "default" | "primary" | "danger", onClick: () => void) {
    const element = document.createElement("button");
    element.type = "button";
    element.className = `pv-btn pv-btn--${variant === "default" ? "plain" : variant}`;
    element.textContent = label;
    element.addEventListener("click", onClick);
    return element;
  }

  function trashButton(label: string, onClick: () => void): HTMLButtonElement {
    const element = document.createElement("button");
    element.type = "button";
    element.className = "pv-icon-btn pv-icon-btn--danger";
    element.title = label;
    element.setAttribute("aria-label", label);
    element.append(kit.icon("trash", label));
    element.addEventListener("click", onClick);
    return element;
  }

  function openPublish(): void {
    if (!projectId || !current?.change) {
      return;
    }
    const change = current.change;
    const { body, footer, close } = modal("Subir rascunho", "Subir rascunho");
    const titleLabel = document.createElement("label");
    titleLabel.textContent = "Título do PR";
    const title = document.createElement("input");
    title.value = stem(change);
    const descriptionLabel = document.createElement("label");
    descriptionLabel.textContent = "Descrição do PR (opcional)";
    const description = document.createElement("textarea");
    const hint = document.createElement("p");
    hint.className = "pv-hint";
    hint.textContent =
      "A mensagem de commit é gerada do título. Cria o fork se preciso e abre/atualiza o PR no GitHub.";
    body.append(titleLabel, title, descriptionLabel, description, hint);

    const cancel = button("Cancelar", "default", close);
    const submit = button("Subir → abrir PR", "primary", () => void run());
    footer.append(cancel, submit);
    const idleHint =
      "A mensagem de commit é gerada do título. Cria o fork se preciso e abre/atualiza o PR no GitHub.";

    async function run(): Promise<void> {
      const value = title.value.trim();
      if (!value) {
        title.focus();
        return;
      }
      cancel.disabled = true;
      submit.disabled = true;
      submit.textContent = "Subindo…";
      hint.textContent = "Sincronizando a base, enviando a branch e abrindo o PR no GitHub…";
      busy(true, "Subindo…");
      try {
        const result = await publishChange(projectId!, change.id, value, description.value);
        close();
        kit.toast({
          message: result.created ? `PR #${result.pr_number} aberto` : `PR #${result.pr_number} atualizado`,
          variant: "success",
        });
        await refresh();
        await options.onReload();
      } catch (error) {
        cancel.disabled = false;
        submit.disabled = false;
        submit.textContent = "Subir → abrir PR";
        hint.textContent = idleHint;
        kit.toast({
          message: error instanceof Error ? error.message : String(error),
          variant: "danger",
        });
      } finally {
        busy(false);
      }
    }
  }

  async function openResume(): Promise<void> {
    if (!projectId) {
      return;
    }
    const { body, close } = modal("Retomar rascunho", "Retomar rascunho");
    const list = document.createElement("div");
    list.className = "pv-change-list";
    const loading = document.createElement("p");
    loading.className = "pv-hint";
    loading.textContent = "Carregando alterações…";
    body.append(list, loading);

    function renderList(): void {
      list.replaceChildren();
      if (changes.length === 0) {
        const empty = document.createElement("p");
        empty.className = "pv-hint";
        empty.textContent = "Nenhuma alteração neste projeto.";
        list.append(empty);
        return;
      }
      for (const change of changes) {
        const row = document.createElement("div");
        row.className = "pv-change-row";
        if (change.id === current?.change?.id) {
          row.classList.add("pv-change-row--current");
        }
        const info = document.createElement("div");
        info.className = "pv-change-info";
        const name = document.createElement("div");
        name.className = "pv-change-name";
        name.textContent = `${stem(change)}${change.pr_number ? ` · PR #${change.pr_number}` : ""}`;
        const meta = document.createElement("div");
        meta.className = "pv-change-meta";
        meta.textContent = statusText(change);
        info.append(name, meta);
        const resumable = change.resumable !== false;
        if (!resumable) {
          const warn = document.createElement("div");
          warn.className = "pv-change-warn";
          warn.textContent = "não é um projeto do previewer — não dá para continuar";
          info.append(warn);
        }
        row.append(info);

        const actions = document.createElement("div");
        actions.className = "pv-change-actions";
        if (change.id !== current?.change?.id) {
          const alter = button("Continuar", "default", () =>
            void runResume(change.id, close, alter),
          );
          if (!resumable) {
            alter.disabled = true;
            alter.title = "não é um projeto do previewer";
          }
          actions.append(alter);
        }
        if (resumable) {
          actions.append(
            trashButton("Abandonar", () => confirmAbandon(change, () => void load())),
          );
        }
        row.append(actions);
        list.append(row);
      }
    }

    async function load(): Promise<void> {
      loading.hidden = false;
      try {
        changes = await listChanges(projectId!, true);
      } catch {
        // mantém a lista atual em caso de falha
      } finally {
        loading.hidden = true;
      }
      renderList();
    }

    await load();
  }

  async function runResume(
    changeId: string,
    close: () => void,
    trigger?: HTMLButtonElement,
  ): Promise<void> {
    if (!projectId) {
      return;
    }
    if (trigger) {
      trigger.disabled = true;
      trigger.textContent = "Abrindo…";
    }
    busy(true, "Abrindo alteração…");
    try {
      await resumeChange(projectId, changeId);
      close();
      await refresh();
      await options.onReload();
    } catch (error) {
      if (trigger) {
        trigger.disabled = false;
        trigger.textContent = "Continuar";
      }
      kit.toast({
        message: error instanceof Error ? error.message : String(error),
        variant: "danger",
      });
    } finally {
      busy(false);
    }
  }

  function openDiscard(): void {
    if (!projectId || !current?.change) {
      return;
    }
    const change = current.change;
    const { body, footer, close } = modal("Descartar rascunho", "Descartar rascunho");
    const message = document.createElement("p");
    message.textContent = `Descartar as edições locais de ${stem(change)} e restaurar a branch?`;
    const hint = document.createElement("p");
    hint.className = "pv-hint";
    hint.textContent = "Volta ao último commit. O PR/branch no remoto não é afetado.";
    body.append(message, hint);
    const confirm = button("Descartar", "danger", () =>
      void runDiscard(change.id, close, confirm),
    );
    footer.append(button("Cancelar", "default", close), confirm);
  }

  async function runDiscard(
    changeId: string,
    close: () => void,
    confirm?: HTMLButtonElement,
  ): Promise<void> {
    if (!projectId) {
      return;
    }
    if (confirm) {
      confirm.disabled = true;
      confirm.textContent = "Descartando…";
    }
    busy(true, "Descartando…");
    try {
      await discardChange(projectId, changeId);
      close();
      await refresh();
      await options.onReload();
    } catch (error) {
      if (confirm) {
        confirm.disabled = false;
        confirm.textContent = "Descartar";
      }
      kit.toast({
        message: error instanceof Error ? error.message : String(error),
        variant: "danger",
      });
    } finally {
      busy(false);
    }
  }

  function confirmAbandon(change: ChangeInfo, onDone?: () => void): void {
    const { body, footer, close } = modal("Abandonar alteração", "Abandonar alteração");
    const message = document.createElement("p");
    message.textContent = `Abandonar ${stem(change)}? A branch local será removida e o PR (se houver) será fechado.`;
    body.append(message);
    const confirm = button("Abandonar", "danger", () =>
      void runAbandon(change.id, close, confirm, onDone),
    );
    footer.append(button("Cancelar", "default", close), confirm);
  }

  async function runAbandon(
    changeId: string,
    close: () => void,
    confirm?: HTMLButtonElement,
    onDone?: () => void,
  ): Promise<void> {
    if (!projectId) {
      return;
    }
    if (confirm) {
      confirm.disabled = true;
      confirm.textContent = "Abandonando…";
    }
    busy(true, "Abandonando…");
    try {
      await abandonChange(projectId, changeId);
      close();
      await refresh();
      await options.onReload();
      onDone?.();
    } catch (error) {
      if (confirm) {
        confirm.disabled = false;
        confirm.textContent = "Abandonar";
      }
      kit.toast({
        message: error instanceof Error ? error.message : String(error),
        variant: "danger",
      });
    } finally {
      busy(false);
    }
  }

  function placeholder(): void {
    current = null;
    changes = [];
    render();
  }

  async function refresh(): Promise<void> {
    if (!projectId) {
      placeholder();
      return;
    }
    try {
      current = await getChangeState(projectId);
    } catch {
      // mantém o estado atual se a consulta falhar (ex.: rede)
    }
    try {
      changes = await listChanges(projectId);
    } catch {
      // mantém a lista atual
    }
    render();
  }

  function setProject(next: string | undefined): void {
    projectId = next;
    current = null;
    changes = [];
    render();
  }

  render();

  return { element, setProject, refresh, backup };
}
