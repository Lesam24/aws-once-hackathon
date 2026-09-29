// Vista lineal de la transcripción, pensada para lectura asistida.
// Cada token braille se acompaña de su descripción legible para lector de pantalla.
import { useState } from "react";
import type { Transcription } from "../types";
import {
  transcriptionSummary,
  transcriptionToPlainText,
} from "../transcriptionText";

interface Props {
  transcription: Transcription;
  onAnnounce?: (message: string, tone?: "info" | "error") => void;
}

function LineList({
  title,
  lines,
}: {
  title: string;
  lines: Transcription["white_lines"];
}) {
  if (lines.length === 0) return null;
  return (
    <section aria-labelledby={`heading-${title}`} className="transcription-group">
      <h3 id={`heading-${title}`}>{title}</h3>
      <ol className="transcription-list">
        {lines.map((line, i) => (
          <li key={`${title}-${i}`}>
            {/* El token braille es el contenido visible; la forma legible se
                anuncia mediante un texto adicional para lectores de pantalla. */}
            <span className="braille-token" lang="und">
              {line.text}
            </span>
            {line.readable ? (
              <span className="line-readable"> {line.readable}</span>
            ) : null}
          </li>
        ))}
      </ol>
    </section>
  );
}

export function TranscriptionView({ transcription, onAnnounce }: Props) {
  const [copied, setCopied] = useState(false);
  const [copiedNarrative, setCopiedNarrative] = useState(false);
  const plain = transcriptionToPlainText(transcription);

  const copyText = async (
    text: string,
    setFlag: (v: boolean) => void,
    label: string
  ) => {
    try {
      await navigator.clipboard.writeText(text);
      setFlag(true);
      onAnnounce?.(`${label} copiada al portapapeles.`);
      window.setTimeout(() => setFlag(false), 3000);
    } catch {
      onAnnounce?.(
        "No se pudo copiar automáticamente. El texto está seleccionable abajo.",
        "error"
      );
    }
  };

  return (
    <div className="transcription">
      {/* Resumen en prosa: lo primero que anuncia el lector de pantalla. */}
      <p className="transcription-summary">{transcriptionSummary(transcription)}</p>

      {/* Descripción en prosa continua, apta para voz o braille. */}
      {transcription.narrative && (
        <section
          aria-labelledby="heading-narrative"
          className="narrative-block"
        >
          <h3 id="heading-narrative">
            <span aria-hidden="true">🗣️</span> Descripción para leer o escuchar
          </h3>
          <p className="narrative-text">{transcription.narrative}</p>
          <div className="transcription-toolbar">
            <button
              type="button"
              className="btn"
              onClick={() =>
                copyText(
                  transcription.narrative,
                  setCopiedNarrative,
                  "Descripción"
                )
              }
            >
              <span aria-hidden="true">📋</span>{" "}
              {copiedNarrative ? "¡Copiada!" : "Copiar descripción"}
            </button>
          </div>
        </section>
      )}

      <div className="transcription-toolbar">
        <button
          type="button"
          className="btn"
          onClick={() => copyText(plain, setCopied, "Transcripción")}
        >
          <span aria-hidden="true">📋</span>{" "}
          {copied ? "¡Copiado!" : "Copiar todo (braille + descripción)"}
        </button>
      </div>

      <LineList title="Blancas" lines={transcription.white_lines} />
      <LineList title="Negras" lines={transcription.black_lines} />

      {transcription.highlights.length > 0 && (
        <section aria-labelledby="heading-highlights" className="transcription-group">
          <h3 id="heading-highlights">Casillas resaltadas</h3>
          <ul>
            {transcription.highlights.map((h, i) => (
              <li key={`hl-${i}`}>{h}</li>
            ))}
          </ul>
        </section>
      )}

      {transcription.arrows.length > 0 && (
        <section aria-labelledby="heading-arrows" className="transcription-group">
          <h3 id="heading-arrows">Flechas</h3>
          <ul>
            {transcription.arrows.map((a, i) => (
              <li key={`ar-${i}`}>{a}</li>
            ))}
          </ul>
        </section>
      )}

      {transcription.warnings.length > 0 && (
        <section
          aria-labelledby="heading-warnings"
          className="transcription-group callout callout--warning"
        >
          <h3 id="heading-warnings">
            <span aria-hidden="true">⚠️</span> Avisos
          </h3>
          <ul className="warnings">
            {transcription.warnings.map((w, i) => (
              <li key={`wn-${i}`}>{w}</li>
            ))}
          </ul>
        </section>
      )}

      {/* Texto plano seleccionable, útil para exportar a un dispositivo braille. */}
      <details className="plain-text">
        <summary>Ver texto plano copiable</summary>
        <textarea
          className="plain-text-area"
          readOnly
          rows={Math.min(20, plain.split("\n").length + 1)}
          value={plain}
          aria-label="Transcripción en texto plano, seleccionable"
        />
      </details>
    </div>
  );
}
