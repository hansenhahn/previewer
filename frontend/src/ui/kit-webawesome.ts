import "@awesome.me/webawesome/dist/components/button/button.js";
import "@awesome.me/webawesome/dist/components/callout/callout.js";
import "@awesome.me/webawesome/dist/components/select/select.js";
import "@awesome.me/webawesome/dist/components/toast/toast.js";

import {
  classNames,
  type ButtonOptions,
  type ButtonVariant,
  type CalloutHandle,
  type CalloutVariant,
  type SelectOptions,
  type Theme,
  type ToastOptions,
  type UiKit,
} from "./kit";

const BUTTON_VARIANT: Record<ButtonVariant, string> = {
  default: "neutral",
  primary: "brand",
  danger: "danger",
};

const CALLOUT_VARIANT: Record<CalloutVariant, string> = {
  neutral: "neutral",
  success: "success",
  warning: "warning",
  danger: "danger",
};

const THEME_STORAGE_KEY = "pv-theme";

type ToastHost = HTMLElement & { create(message: string, options?: object): void };

let toastElement: ToastHost | undefined;

function toastHost(): ToastHost {
  if (!toastElement) {
    toastElement = document.createElement("wa-toast") as ToastHost;
    document.body.append(toastElement);
  }
  return toastElement;
}

function button(options: ButtonOptions): HTMLElement {
  const element = document.createElement("wa-button");
  element.setAttribute("variant", BUTTON_VARIANT[options.variant ?? "default"]);
  element.className = classNames("pv-button", `pv-button--${options.variant ?? "default"}`);
  element.textContent = options.label;
  if (options.disabled) {
    element.setAttribute("disabled", "");
  }
  element.addEventListener("click", options.onClick);
  return element;
}

function select(options: SelectOptions): HTMLElement {
  const element = document.createElement("wa-select") as HTMLElement & { value: string };
  if (options.label) {
    element.setAttribute("label", options.label);
  }
  for (const option of options.options) {
    const item = document.createElement("wa-option");
    item.setAttribute("value", option.value);
    item.textContent = option.label;
    if (option.value === options.value) {
      item.setAttribute("selected", "");
    }
    element.append(item);
  }
  element.addEventListener("change", () => options.onChange(element.value));
  return element;
}

function icon(name: string, label?: string): HTMLElement {
  const element = document.createElement("wa-icon");
  element.setAttribute("name", name);
  if (label) {
    element.setAttribute("label", label);
  }
  return element;
}

function callout(message: string, variant: CalloutVariant = "neutral"): CalloutHandle {
  const element = document.createElement("wa-callout");
  element.setAttribute("variant", CALLOUT_VARIANT[variant]);
  const text = document.createElement("span");
  text.textContent = message;
  element.append(text);
  return {
    element,
    setMessage(next: string, nextVariant?: CalloutVariant) {
      text.textContent = next;
      if (nextVariant) {
        element.setAttribute("variant", CALLOUT_VARIANT[nextVariant]);
      }
    },
    hide() {
      element.hidden = true;
    },
  };
}

function toast(options: ToastOptions): void {
  toastHost().create(options.message, {
    variant: CALLOUT_VARIANT[options.variant ?? "success"],
    duration: options.duration ?? 3000,
  });
}

function resolveTheme(theme: Theme): "light" | "dark" {
  if (theme === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return theme;
}

function applyTheme(theme: Theme): void {
  const resolved = resolveTheme(theme);
  const root = document.documentElement;
  root.dataset.theme = resolved;
  root.classList.toggle("wa-dark", resolved === "dark");
  root.classList.toggle("wa-light", resolved === "light");
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    // armazenamento indisponível: ignora
  }
}

export const kit: UiKit = { button, select, icon, callout, toast, applyTheme };
