// Utilidades para convertir una transcripción en texto plano copiable
// (compatible con líneas braille) y en un resumen legible para lectores de pantalla.
import type { Transcription } from "./types";

/** Texto plano copiable: braille en formato ONCE + descripción en prosa. */
export function transcriptionToPlainText(t: Transcription): string {
  const parts: string[] = [];
  // El bloque braille en formato ONCE es la salida principal.
  if (t.braille_block) {
    parts.push(t.braille_block);
  }
  if (t.warnings.length) {
    parts.push("", "Avisos:");
    parts.push(...t.warnings);
  }
  if (t.narrative) {
    parts.push("", "Descripción:", t.narrative);
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
