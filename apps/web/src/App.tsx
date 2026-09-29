import { useCallback, useState } from "react";
import {
  confirmResult,
  createAnalysis,
  getAnalysis,
  submitCorrection,
} from "./api";
import { CorrectionEditor } from "./components/CorrectionEditor";
import { HistoryView } from "./components/HistoryView";
import { StatusAnnouncer } from "./components/StatusAnnouncer";
import { TranscriptionView } from "./components/TranscriptionView";
import type { AccessMode, Analysis, BoardState } from "./types";

type View = "analyze" | "history";

export default function App() {
  const [mode, setMode] = useState<AccessMode>("blind");
  const [view, setView] = useState<View>("analyze");
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [historyKey, setHistoryKey] = useState(0);

  const clearMessages = () => {
    setStatus("");
    setError("");
  };

  const onAnalyze = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      clearMessages();
      if (!file) {
        setError("Selecciona una imagen del tablero antes de analizar.");
        return;
      }
      setBusy(true);
      setStatus("Analizando la imagen del tablero…");
      try {
        const result = await createAnalysis(file, mode);
        setAnalysis(result);
        if (result.status === "failed") {
          setError(result.error ?? "El análisis ha fallado.");
        } else {
          setStatus("Análisis completado. La transcripción está disponible.");
        }
        setHistoryKey((k) => k + 1);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setBusy(false);
      }
    },
    [file, mode]
  );

  const onConfirm = useCallback(async () => {
    if (!analysis) return;
    setBusy(true);
    clearMessages();
    try {
      await confirmResult(analysis.id);
      setStatus("Confirmación registrada. Gracias por tu revisión.");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }, [analysis]);

  const onSubmitCorrection = useCallback(
    async (corrected: BoardState) => {
      if (!analysis) return;
      setBusy(true);
      clearMessages();
      try {
        await submitCorrection(analysis.id, corrected);
        setStatus(
          "Corrección enviada. Pasará por revisión antes de usarse para mejorar el modelo."
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setBusy(false);
      }
    },
    [analysis]
  );

  const openFromHistory = useCallback(async (id: string) => {
    setBusy(true);
    clearMessages();
    try {
      const result = await getAnalysis(id);
      setAnalysis(result);
      setView("analyze");
      setStatus("Análisis cargado desde el historial.");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }, []);

  return (
    <>
      <a href="#main" className="skip-link">
        Saltar al contenido principal
      </a>

      <header>
        <h1>Chess Accessibility</h1>
        <p>
          Convierte una imagen de un tablero de ajedrez en una transcripción braille
          accesible.
        </p>
        <nav aria-label="Secciones">
          <button
            type="button"
            aria-current={view === "analyze" ? "page" : undefined}
            onClick={() => setView("analyze")}
          >
            Analizar
          </button>
          <button
            type="button"
            aria-current={view === "history" ? "page" : undefined}
            onClick={() => setView("history")}
          >
            Historial
          </button>
        </nav>
      </header>

      <main id="main">
        <StatusAnnouncer message={error || status} tone={error ? "error" : "info"} />

        {view === "analyze" && (
          <>
            <section aria-labelledby="upload-heading">
              <h2 id="upload-heading">1. Sube una imagen y elige el modo</h2>
              <form onSubmit={onAnalyze}>
                <fieldset>
                  <legend>Modo de uso</legend>
                  <label>
                    <input
                      type="radio"
                      name="mode"
                      value="blind"
                      checked={mode === "blind"}
                      onChange={() => setMode("blind")}
                    />
                    Ciego (lectura directa, sin edición)
                  </label>
                  <label>
                    <input
                      type="radio"
                      name="mode"
                      value="sighted"
                      checked={mode === "sighted"}
                      onChange={() => setMode("sighted")}
                    />
                    Vidente (revisión y corrección)
                  </label>
                </fieldset>

                <p>
                  <label htmlFor="image">Imagen del tablero</label>
                  <input
                    id="image"
                    type="file"
                    accept="image/*"
                    onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  />
                </p>

                <button type="submit" disabled={busy}>
                  {busy ? "Procesando…" : "Analizar tablero"}
                </button>
              </form>
            </section>

            {analysis?.transcription && (
              <section aria-labelledby="result-heading">
                <h2 id="result-heading">2. Transcripción</h2>
                <TranscriptionView transcription={analysis.transcription} />

                {mode === "sighted" && analysis.board_state && (
                  <>
                    <h2>3. Revisión y corrección</h2>
                    <CorrectionEditor
                      board={analysis.board_state}
                      onConfirm={onConfirm}
                      onSubmitCorrection={onSubmitCorrection}
                      busy={busy}
                    />
                  </>
                )}
              </section>
            )}

            {analysis?.status === "failed" && (
              <section aria-labelledby="failed-heading">
                <h2 id="failed-heading">No se pudo analizar la imagen</h2>
                <p>{analysis.error}</p>
              </section>
            )}
          </>
        )}

        {view === "history" && (
          <section aria-labelledby="history-heading">
            <h2 id="history-heading">Historial</h2>
            <HistoryView onOpen={openFromHistory} refreshKey={historyKey} />
          </section>
        )}
      </main>

      <footer>
        <p>
          Transcripción basada en la signografía braille de la Comisión Braille Española
          (Reto Ajedrez ONCE).
        </p>
      </footer>
    </>
  );
}
