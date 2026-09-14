import { getAuthConfig, type AuthConfig } from "./api";
import { kit } from "./ui";

export async function loadAuthConfig(): Promise<AuthConfig> {
  return getAuthConfig();
}

export function renderLogin(
  host: HTMLElement,
  config: AuthConfig,
  message?: string,
): void {
  host.replaceChildren();

  const card = document.createElement("div");
  card.className = "login-card";

  const brand = document.createElement("h1");
  brand.className = "login-brand";
  brand.textContent = "previewer";

  const notice = document.createElement("p");
  notice.className = "login-message";
  notice.textContent =
    message ?? "Acesso restrito. Entre com sua conta autorizada para continuar.";

  const actions = document.createElement("div");
  actions.className = "login-actions";

  const button = kit.button({
    label: `Entrar com ${config.label}`,
    variant: "primary",
    onClick: () => {
      window.location.assign(config.login_url);
    },
  });
  button.classList.add("login-button");
  actions.append(button);

  card.append(brand, notice, actions);
  host.append(card);
  host.hidden = false;
}
