// Cliente de la API. La base se configura con VITE_API_BASE.
import type { Analysis, BoardState, HistoryItem } from "./types";

const API_BASE: string =
  (import.meta.env.VITE_API_BASE as string | undefined) ??
  "http://localhost:8000/api/v1";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Error ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = String(body.detail);
    } catch {
      /* respuesta sin cuerpo JSON */
    }
    throw new Error(detail);
  }
  return (await res.json()) as T;
}

export async function createAnalysis(
  image: File,
  mode: "blind" | "sighted"
): Promise<Analysis> {
  const form = new FormData();
  form.append("image", image);
  form.append("mode", mode);
  const res = await fetch(`${API_BASE}/analyses`, {
    method: "POST",
    body: form,
  });
  const data = await handle<{ analysis: Analysis }>(res);
  return data.analysis;
}

export async function getAnalysis(id: string): Promise<Analysis> {
  const res = await fetch(`${API_BASE}/analyses/${id}`);
  const data = await handle<{ analysis: Analysis }>(res);
  return data.analysis;
}

export async function submitCorrection(
  id: string,
  correctedBoardState: BoardState,
  userId?: string
): Promise<void> {
  const res = await fetch(`${API_BASE}/analyses/${id}/correction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      corrected_board_state: correctedBoardState,
      user_id: userId,
    }),
  });
  await handle(res);
}

export async function confirmResult(id: string, userId?: string): Promise<void> {
  const res = await fetch(`${API_BASE}/analyses/${id}/feedback/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId }),
  });
  await handle(res);
}

export async function getHistory(): Promise<HistoryItem[]> {
  const res = await fetch(`${API_BASE}/history`);
  const data = await handle<{ items: HistoryItem[] }>(res);
  return data.items;
}
