import { basicSetup, EditorView } from "codemirror";

export interface EditorHandle {
  getText(): string;
  setText(text: string): void;
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

  return {
    getText: () => view.state.doc.toString(),
    setText: (text: string) => {
      view.dispatch({
        changes: { from: 0, to: view.state.doc.length, insert: text },
      });
    },
  };
}
