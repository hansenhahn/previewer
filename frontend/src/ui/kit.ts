export type ButtonVariant = "default" | "primary" | "danger";
export type CalloutVariant = "neutral" | "success" | "warning" | "danger";
export type Theme = "light" | "dark" | "system";

export interface ButtonOptions {
  label: string;
  onClick: () => void;
  variant?: ButtonVariant;
  disabled?: boolean;
}

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectOptions {
  options: SelectOption[];
  value?: string;
  label?: string;
  onChange: (value: string) => void;
}

export interface ToastOptions {
  message: string;
  variant?: CalloutVariant;
  duration?: number;
}

export interface CalloutHandle {
  element: HTMLElement;
  setMessage(message: string, variant?: CalloutVariant): void;
  hide(): void;
}

export interface MenuItem {
  label: string;
  onSelect: () => void;
  icon?: string;
  danger?: boolean;
}

export interface MenuOptions {
  trigger: HTMLElement;
  header?: HTMLElement;
  items: MenuItem[];
}

export interface MenuHandle {
  element: HTMLElement;
  open(): void;
  close(): void;
}

export interface UiKit {
  button(options: ButtonOptions): HTMLElement;
  select(options: SelectOptions): HTMLElement;
  icon(name: string, label?: string): HTMLElement;
  menu(options: MenuOptions): MenuHandle;
  callout(message: string, variant?: CalloutVariant): CalloutHandle;
  toast(options: ToastOptions): void;
  applyTheme(theme: Theme): void;
}

export function classNames(...values: Array<string | false | null | undefined>): string {
  return values.filter(Boolean).join(" ");
}

export function variantClass(base: string, variant?: string): string {
  if (!variant || variant === "default") {
    return base;
  }
  return classNames(base, `${base}--${variant}`);
}
