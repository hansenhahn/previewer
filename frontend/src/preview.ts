import { atlasImageUrl, backgroundUrl, getAtlas } from "./api";
import type { AtlasMetrics, Screen } from "./api";
import { computeLayout } from "./layout";
import { buildDrawCommands } from "./render";

export const SCREEN_WIDTH = 256;
export const SCREEN_HEIGHT = 192;

function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`falha ao carregar ${url}`));
    image.src = url;
  });
}

export class Preview {
  private readonly canvas: HTMLCanvasElement;
  private readonly context: CanvasRenderingContext2D;
  private readonly backgroundCache = new Map<string, HTMLImageElement>();
  private projectId?: string;
  private screen?: Screen;
  private matches: string[] = [];
  private tags: string[] = [];
  private font?: string;
  private atlas?: AtlasMetrics;
  private atlasImage?: HTMLImageElement;
  private backgroundImage?: HTMLImageElement;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    const context = canvas.getContext("2d");
    if (!context) {
      throw new Error("contexto 2d indisponível");
    }
    this.context = context;
    this.context.imageSmoothingEnabled = false;
  }

  async configure(
    projectId: string,
    screen: Screen,
    matches: string[],
    tags: string[],
  ): Promise<void> {
    this.projectId = projectId;
    this.screen = screen;
    this.matches = matches;
    this.tags = tags;

    if (this.font !== screen.font || !this.atlas) {
      this.font = screen.font;
      this.atlas = await getAtlas(projectId, screen.font);
      this.atlasImage = await loadImage(atlasImageUrl(projectId, screen.font));
    }
    this.backgroundImage = await this.getBackground(
      backgroundUrl(projectId, screen.background),
    );
  }

  render(text: string): void {
    if (!this.projectId || !this.screen || !this.atlas || !this.atlasImage) {
      return;
    }
    const context = this.context;
    context.clearRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

    if (this.backgroundImage) {
      context.drawImage(this.backgroundImage, 0, 0);
    }

    const result = computeLayout(
      text,
      this.screen,
      this.atlas,
      this.matches,
      this.tags,
    );
    for (const command of buildDrawCommands(result.glyphs, this.atlas)) {
      context.drawImage(
        this.atlasImage,
        command.sx,
        command.sy,
        command.sw,
        command.sh,
        command.dx,
        command.dy,
        command.sw,
        command.sh,
      );
    }
  }

  setZoom(scale: number): void {
    this.canvas.style.width = `${SCREEN_WIDTH * scale}px`;
    this.canvas.style.height = `${SCREEN_HEIGHT * scale}px`;
  }

  private async getBackground(url: string): Promise<HTMLImageElement | undefined> {
    const cached = this.backgroundCache.get(url);
    if (cached) {
      return cached;
    }
    try {
      const image = await loadImage(url);
      this.backgroundCache.set(url, image);
      return image;
    } catch {
      return undefined;
    }
  }
}
