// Utilidades para convertir una transcripción en texto plano copiable
// (compatible con líneas braille) y en un resumen legible para lectores de pantalla.
import type { Transcription } from "./types";

/** Texto plano con los tokens braille, una línea por pieza. */
export function transcriptionToPlainText(t: Transcription): string {
  const parts: string[] = [];
  if (t.narrative) {
    parts.push("Descripción:", t.narrative, "");
  }
  if (t.white_lines.length) {
    parts.push("Blancas:");
    parts.push(...t.white_lines.map((l) => l.text));
  }
  if (t.black_lines.length) {
    parts.push("", "Negras:");
    parts.push(...t.black_lines.map((l) => l.text));
  }
  if (t.highlights.length) {
    parts.push("", "Resaltadas:");
    parts.push(...t.highlights);
  }
  if (t.arrows.length) {
    parts.push("", "Flechas:");
    parts.push(...t.arrows);
  }
  if (t.warnings.length) {
    parts.push("", "Avisos:");
    parts.push(...t.warnings);
  }
  return parts.join("\n");
}

/** Resumen en prosa para anunciar por lector de pantalla. */
export function transcriptionSummary(t: Transcription): string {
  const w = t.white_lines.length;
  const b = t.black_lines.length;
  const pieces = w + b;
  let summary = `Transcripción lista. ${pieces} piezas en total: ${w} blancas y ${b} negras.`;
  if (t.warnings.length) {
    summary += ` ${t.warnings.length} ${
      t.warnings.length === 1 ? "aviso" : "avisos"
    } de fiabilidad.`;
  }
  return summary;
}
