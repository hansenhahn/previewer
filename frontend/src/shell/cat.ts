import { classNames, kit } from "../ui";
import {
  align,
  reconstruct,
  segment,
  segmentBody,
  segmentsOf,
  type AlignedPair,
  type Part,
} from "../segmentation";

export interface CatOptions {
  onTranslatedChange: (text: string) => void;
  onSelect?: (startLine: number) => void;
}

export interface CatController {
  element: HTMLElement;
  load(translated: string, original: string | null, start: string[], end: string[]): void;
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
  let boxes: HTMLElement[] = [];
  let active = 0;

  function autoGrow(textarea: HTMLTextAreaElement): void {
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  function setActive(index: number): void {
    active = index;
    boxes.forEach((box, i) => box.classList.toggle("active", i === index));
    const box = boxes[index];
    if (box) {
      box.scrollIntoView({ block: "nearest" });
    }
    const pair = pairs[index];
    const startLine = pair?.translated?.startLine ?? pair?.original?.startLine;
    if (startLine !== undefined) {
      options.onSelect?.(startLine);
    }
  }

  function focusSegment(index: number): void {
    setActive(index);
    const textarea = boxes[index]?.querySelector("textarea");
    if (textarea) {
      textarea.focus();
    }
  }

  function move(delta: number): void {
    focusSegment(Math.max(0, Math.min(boxes.length - 1, active + delta)));
  }

  function load(
    translated: string,
    original: string | null,
    start: string[],
    end: string[],
  ): void {
    element.replaceChildren();
    boxes = [];
    active = 0;
    pairs = [];
    translatedParts = [];

    if (start.length === 0) {
      const message = document.createElement("p");
      message.className = "pv-muted";
      message.textContent = "Segmentação não configurada para este projeto.";
      element.append(message);
      return;
    }

    translatedParts = segment(translated, start, end);
    const originalParts = original ? segment(original, start, end) : [];
    pairs = align(originalParts, translatedParts);
    const originalCount = segmentsOf(originalParts).length;
    const translatedCount = segmentsOf(translatedParts).length;

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

    const growth: Array<() => void> = [];

    pairs.forEach((pair, index) => {
      const box = document.createElement("div");
      box.className = "pv-cat-box";
      box.id = `cat-box-${index}`;
      box.addEventListener("mousedown", () => setActive(index));

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
        growth.push(() => autoGrow(textarea));
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

      boxes.push(box);
      element.append(box);
    });

    growth.forEach((grow) => grow());
    if (boxes.length > 0) {
      setActive(0);
    }
  }

  return { element, load, focusSegment, move };
}
