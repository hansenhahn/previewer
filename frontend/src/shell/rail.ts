import { classNames, kit } from "../ui";

export type SectionId = "projects" | "files";

export interface RailSection {
  id: SectionId;
  label: string;
  icon: string;
}

export const RAIL_SECTIONS: RailSection[] = [
  { id: "projects", label: "Projetos", icon: "folder" },
  { id: "files", label: "Arquivos", icon: "file-lines" },
];

export function renderRail(
  container: HTMLElement,
  sections: RailSection[],
  active: SectionId,
  onSelect: (id: SectionId) => void,
): void {
  container.replaceChildren();
  for (const section of sections) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = classNames("pv-rail-item", section.id === active && "active");
    const label = document.createElement("span");
    label.textContent = section.label;
    button.append(kit.icon(section.icon, section.label), label);
    button.addEventListener("click", () => onSelect(section.id));
    container.append(button);
  }
}
