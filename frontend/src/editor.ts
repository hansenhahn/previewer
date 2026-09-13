import { basicSetup, EditorView } from "codemirror";
import { EditorState } from "@codemirror/state";

export interface EditorHandle {
  getText(): string;
  setText(text: string): void;
  requestMeasure(): void;
}

function handle(view: EditorView): EditorHandle {
  return {
    getText: () => view.state.doc.toString(),
    setText: (text: string) => {
      view.dispatch({
        changes: { from: 0, to: view.state.doc.length, insert: text },
      });
    },
    requestMeasure: () => view.requestMeasure(),
  };
}

export function createEditor(parent: HTMLElement, onChange: () => void): EditorHandle {
  const view = new EditorView({
    doc: "",
    extensions: [
      basicSetup,
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          onChange();
        }
      }),
    ],
    parent,
  });

  return handle(view);
}

export function createReadOnlyEditor(parent: HTMLElement): EditorHandle {
  const view = new EditorView({
    doc: "",
    extensions: [
      basicSetup,
      EditorState.readOnly.of(true),
      EditorView.editable.of(false),
    ],
    parent,
  });

  return handle(view);
}
