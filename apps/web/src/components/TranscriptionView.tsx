// Vista lineal de la transcripción, pensada para lectura asistida.
// Cada token braille se acompaña de su descripción legible para lector de pantalla.
import type { Transcription } from "../types";

interface Props {
  transcription: Transcription;
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
    <section aria-labelledby={`heading-${title}`}>
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
              <span className="visually-hidden">, {line.readable}</span>
            ) : null}
          </li>
        ))}
      </ol>
    </section>
  );
}

export function TranscriptionView({ transcription }: Props) {
  return (
    <div className="transcription">
      <LineList title="Blancas" lines={transcription.white_lines} />
      <LineList title="Negras" lines={transcription.black_lines} />

      {transcription.highlights.length > 0 && (
        <section aria-labelledby="heading-highlights">
          <h3 id="heading-highlights">Casillas resaltadas</h3>
          <ul>
            {transcription.highlights.map((h, i) => (
              <li key={`hl-${i}`}>{h}</li>
            ))}
          </ul>
        </section>
      )}

      {transcription.arrows.length > 0 && (
        <section aria-labelledby="heading-arrows">
          <h3 id="heading-arrows">Flechas</h3>
          <ul>
            {transcription.arrows.map((a, i) => (
              <li key={`ar-${i}`}>{a}</li>
            ))}
          </ul>
        </section>
      )}

      {transcription.warnings.length > 0 && (
        <section aria-labelledby="heading-warnings">
          <h3 id="heading-warnings">Avisos</h3>
          <ul className="warnings">
            {transcription.warnings.map((w, i) => (
              <li key={`wn-${i}`}>{w}</li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
