import type { AuthConfig, AuthUser } from "../api";
import { kit } from "../ui";

export function renderAccount(
  host: HTMLElement,
  user: AuthUser,
  config: AuthConfig,
): void {
  host.replaceChildren();

  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.className = "pv-account";

  const name = document.createElement("span");
  name.className = "pv-account-name";
  name.textContent = user.login;
  trigger.append(name);

  const header = document.createElement("div");
  header.className = "pv-account-head";
  if (user.avatar_url) {
    const photo = document.createElement("img");
    photo.className = "pv-account-photo";
    photo.alt = "";
    photo.src = user.avatar_url;
    header.append(photo);
  }
  const info = document.createElement("div");
  info.className = "pv-account-info";
  const login = document.createElement("strong");
  login.textContent = user.login;
  info.append(login);
  if (user.email) {
    const email = document.createElement("span");
    email.className = "pv-account-email";
    email.textContent = user.email;
    info.append(email);
  }
  const provider = document.createElement("span");
  provider.className = "pv-account-provider";
  provider.textContent = `via ${config.label}`;
  info.append(provider);
  header.append(info);

  const menu = kit.menu({
    trigger,
    header,
    items: [
      {
        label: "Sair",
        icon: "arrow-right-from-bracket",
        danger: true,
        onSelect: () => window.location.assign("/auth/logout"),
      },
    ],
  });
  host.append(menu.element);
}
