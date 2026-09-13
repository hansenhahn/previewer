export interface OpenDocument {
  path: string;
  content: string;
  original: string | null;
  modified: boolean;
}

export function findDocument(
  documents: OpenDocument[],
  path: string,
): OpenDocument | undefined {
  return documents.find((document) => document.path === path);
}

export function addDocument(
  documents: OpenDocument[],
  document: OpenDocument,
): OpenDocument[] {
  if (findDocument(documents, document.path)) {
    return documents;
  }
  return [...documents, document];
}

export function closeDocument(
  documents: OpenDocument[],
  path: string,
): OpenDocument[] {
  return documents.filter((document) => document.path !== path);
}

export function updateContent(
  documents: OpenDocument[],
  path: string,
  content: string,
): OpenDocument[] {
  return documents.map((document) =>
    document.path === path ? { ...document, content } : document,
  );
}

export function markModified(
  documents: OpenDocument[],
  path: string,
  content: string,
): OpenDocument[] {
  return documents.map((document) =>
    document.path === path ? { ...document, content, modified: true } : document,
  );
}

export function markSaved(
  documents: OpenDocument[],
  path: string,
  content: string,
): OpenDocument[] {
  return documents.map((document) =>
    document.path === path ? { ...document, content, modified: false } : document,
  );
}

export function pathAfterClose(
  documents: OpenDocument[],
  path: string,
): string | undefined {
  const index = documents.findIndex((document) => document.path === path);
  const remaining = closeDocument(documents, path);
  if (remaining.length === 0) {
    return undefined;
  }
  const nextIndex = index === -1 ? 0 : Math.min(index, remaining.length - 1);
  return remaining[nextIndex].path;
}
