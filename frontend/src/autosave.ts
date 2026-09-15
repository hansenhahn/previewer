export type SaveState = "idle" | "saving" | "saved" | "offline";

export interface AutosaveOptions {
  save: () => Promise<void>;
  onState: (state: SaveState) => void;
  delay?: number;
  retryDelay?: number;
}

export interface Autosave {
  schedule(): void;
  flush(): Promise<void>;
  state(): SaveState;
  cancel(): void;
}

export function createAutosave(options: AutosaveOptions): Autosave {
  const delay = options.delay ?? 60000;
  const retryDelay = options.retryDelay ?? 4000;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let state: SaveState = "idle";

  function setState(next: SaveState): void {
    state = next;
    options.onState(next);
  }

  function clearTimer(): void {
    if (timer !== undefined) {
      clearTimeout(timer);
      timer = undefined;
    }
  }

  async function run(): Promise<void> {
    setState("saving");
    try {
      await options.save();
      setState("saved");
    } catch {
      setState("offline");
      clearTimer();
      timer = setTimeout(() => {
        timer = undefined;
        void run();
      }, retryDelay);
    }
  }

  function schedule(): void {
    clearTimer();
    timer = setTimeout(() => {
      timer = undefined;
      void run();
    }, delay);
  }

  async function flush(): Promise<void> {
    clearTimer();
    await run();
  }

  return {
    schedule,
    flush,
    state: () => state,
    cancel: clearTimer,
  };
}
