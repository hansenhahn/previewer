import { kit } from "../ui";
import {
  align,
  reconstruct,
  segment,
  segmentBody,
  segmentBySeparators,
  segmentsOf,
  type AlignedPair,
  type Part,
} from "../segmentation";

export interface CatOptions {
  onTranslatedChange: (text: string) => void;
  onSelect?: (startLine: number) => void;
  onOpen?: (index: number) => void;
}

export interface CatController {
  element: HTMLElement;
  load(
    translated: string,
    original: string | null,
    start: string[],
    end: string[],
    separators?: string[],
  ): void;
  setBrowse(enabled: boolean): void;
  showList(): void;
  focus(index: number): void;
  count(): number;
  activeIndex(): number;
  activeStartLine(): number | undefined;
  focusSegment(index: number): void;
  move(delta: number): void;
}

const STATUS_LABELS = {
  done: "traduzido",
  empty: "vazio",
  missing: "sem tradução",
} as const;

export function createCat(options: CatOptions): CatController {
  const element = document.createElement("div");
  element.className = "pv-cat";

  let translatedParts: Part[] = [];
  let pairs: AlignedPair[] = [];
  let boxes: Array<{ index: number; el: HTMLElement }> = [];
  let originalCount = 0;
  let translatedCount = 0;
  let active = 0;
  let browse = false;
  let focusIndex: number | null = null;

  function autoGrow(textarea: HTMLTextAreaElement): void {
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  function boxFor(index: number): HTMLElement | undefined {
    return boxes.find((box) => box.index === index)?.el;
  }

  function setActive(index: number): void {
    active = index;
    boxes.forEach((box) => box.el.classList.toggle("active", box.index === index));
    boxFor(index)?.scrollIntoView({ block: "nearest" });
    const pair = pairs[index];
    const startLine = pair?.translated?.startLine ?? pair?.original?.startLine;
    if (startLine !== undefined) {
      options.onSelect?.(startLine);
    }
  }

  function focusSegment(index: number): void {
    setActive(index);
    boxFor(index)?.querySelector("textarea")?.focus();
  }

  function move(delta: number): void {
    const next = Math.max(0, Math.min(pairs.length - 1, active + delta));
    if (focusIndex !== null) {
      focus(next);
    } else {
      focusSegment(next);
    }
  }

  function renderBox(index: number, pair: AlignedPair): void {
    const editable = !browse && (focusIndex === null || focusIndex === index);
    const box = document.createElement("div");
    box.className = "pv-cat-box";
    box.id = `cat-box-${index}`;
    box.addEventListener("mousedown", () => setActive(index));
    if (browse) {
      box.addEventListener("dblclick", () => options.onOpen?.(index));
    }

    const boxHead = document.createElement("div");
    boxHead.className = "pv-cat-box-head";
    const number = document.createElement("span");
    number.className = "pv-cat-index";
    number.textContent = `#${index + 1}`;
    boxHead.append(number);

    const badge = document.createElement("span");
    if (!pair.translated) {
      badge.className = "pv-badge pv-badge--missing";
      badge.textContent = STATUS_LABELS.missing;
    } else if (segmentBody(pair.translated).trim().length === 0) {
      badge.className = "pv-badge pv-badge--empty";
      badge.textContent = STATUS_LABELS.empty;
    } else {
      badge.className = "pv-badge pv-badge--done";
      badge.textContent = STATUS_LABELS.done;
    }
    boxHead.append(badge);
    box.append(boxHead);

    const body = document.createElement("div");
    body.className = "pv-cat-box-body";

    const source = document.createElement("p");
    source.className = "pv-cat-original";
    source.textContent = pair.original ? segmentBody(pair.original) : "(sem original)";
    body.append(source);

    const count = document.createElement("span");
    count.className = "pv-cat-count";

    if (pair.translated) {
      const translatedSegment = pair.translated;
      if (editable) {
        const target = document.createElement("div");
        target.className = "pv-cat-target";
        const textarea = document.createElement("textarea");
        textarea.className = "pv-cat-translated";
        textarea.value = segmentBody(translatedSegment);
        const updateCount = (): void => {
          count.textContent = `${textarea.value.length} caracteres`;
        };
        textarea.addEventListener("focus", () => setActive(index));
        textarea.addEventListener("input", () => {
          translatedSegment.bodyLines = textarea.value.split("\n");
          autoGrow(textarea);
          updateCount();
          options.onTranslatedChange(reconstruct(translatedParts));
        });
        target.append(textarea);
        body.append(target);
        updateCount();
      } else {
        const text = document.createElement("div");
        text.className = "pv-cat-translated pv-cat-readonly";
        text.textContent = segmentBody(translatedSegment);
        body.append(text);
        count.textContent = `${segmentBody(translatedSegment).length} caracteres`;
      }
    } else {
      const note = document.createElement("p");
      note.className = "pv-muted";
      note.textContent = "sem segmento traduzido correspondente";
      body.append(note);
    }

    box.append(body);

    const foot = document.createElement("div");
    foot.className = "pv-cat-box-foot";
    foot.append(count);
    box.append(foot);

    boxes.push({ index, el: box });
    element.append(box);
  }

  function render(): void {
    element.replaceChildren();
    boxes = [];

    if (focusIndex !== null) {
      const pair = pairs[focusIndex];
      if (pair) {
        renderBox(focusIndex, pair);
      }
    } else {
      const header = document.createElement("div");
      header.className = "pv-cat-head";
      if (originalCount !== translatedCount) {
        const callout = kit.callout(
          `Alinhamento: ${originalCount} original × ${translatedCount} traduzido — há blocos sem par.`,
          "warning",
        );
        header.append(callout.element);
      }
      if (header.childElementCount > 0) {
        element.append(header);
      }
      pairs.forEach((pair, index) => renderBox(index, pair));
    }

    if (boxes.length > 0) {
      setActive(focusIndex ?? 0);
    }

    for (const box of boxes) {
      const textarea = box.el.querySelector("textarea");
      if (textarea) {
        autoGrow(textarea as HTMLTextAreaElement);
      }
    }
  }

  function load(
    translated: string,
    original: string | null,
    start: string[],
    end: string[],
    separators: string[] = [],
  ): void {
    focusIndex = null;
    pairs = [];
    translatedParts = [];

    if (start.length === 0 && separators.length === 0) {
      element.replaceChildren();
      boxes = [];
      const message = document.createElement("p");
      message.className = "pv-muted";
      message.textContent = "Segmentação não configurada para este projeto.";
      element.append(message);
      return;
    }

    const split = (value: string): Part[] =>
      separators.length > 0
        ? segmentBySeparators(value, separators)
        : segment(value, start, end);

    translatedParts = split(translated);
    const originalParts = original ? split(original) : [];
    pairs = align(originalParts, translatedParts);
    originalCount = segmentsOf(originalParts).length;
    translatedCount = segmentsOf(translatedParts).length;
    render();
  }

  function setBrowse(enabled: boolean): void {
    if (browse === enabled) {
      return;
    }
    browse = enabled;
    render();
  }

  function showList(): void {
    focusIndex = null;
    browse = true;
    render();
  }

  function focus(index: number): void {
    focusIndex = index;
    browse = false;
    render();
  }

  return {
    element,
    load,
    setBrowse,
    showList,
    focus,
    count: () => pairs.length,
    activeIndex: () => active,
    activeStartLine: () =>
      pairs[active]?.translated?.startLine ?? pairs[active]?.original?.startLine,
    focusSegment,
    move,
  };
}
