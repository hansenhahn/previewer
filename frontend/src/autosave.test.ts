import { describe, expect, it, vi } from "vitest";

import { createAutosave } from "./autosave";

describe("autosave", () => {
  it("salva após o debounce e emite os estados", async () => {
    vi.useFakeTimers();
    const save = vi.fn().mockResolvedValue(undefined);
    const states: string[] = [];
    const autosave = createAutosave({
      save,
      onState: (state) => states.push(state),
      delay: 100,
    });
    autosave.schedule();
    expect(save).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(100);
    expect(save).toHaveBeenCalledTimes(1);
    expect(states).toEqual(["saving", "saved"]);
    vi.useRealTimers();
  });

  it("informa offline e tenta novamente", async () => {
    vi.useFakeTimers();
    const save = vi
      .fn()
      .mockRejectedValueOnce(new Error("sem rede"))
      .mockResolvedValue(undefined);
    const states: string[] = [];
    const autosave = createAutosave({
      save,
      onState: (state) => states.push(state),
      delay: 100,
      retryDelay: 200,
    });
    autosave.schedule();
    await vi.advanceTimersByTimeAsync(100);
    expect(states).toContain("offline");
    await vi.advanceTimersByTimeAsync(200);
    expect(save).toHaveBeenCalledTimes(2);
    expect(states[states.length - 1]).toBe("saved");
    vi.useRealTimers();
  });

  it("flush salva imediatamente e cancela o timer", async () => {
    vi.useFakeTimers();
    const save = vi.fn().mockResolvedValue(undefined);
    const autosave = createAutosave({ save, onState: () => {}, delay: 1000 });
    autosave.schedule();
    await autosave.flush();
    expect(save).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(1000);
    expect(save).toHaveBeenCalledTimes(1);
    vi.useRealTimers();
  });
});
