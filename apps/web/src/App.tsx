import { useCallback, useEffect, useRef, useState } from "react";
import {
  confirmResult,
  createAnalysis,
  getAnalysis,
  submitCorrection,
} from "./api";
import { CorrectionEditor } from "./components/CorrectionEditor";
import { HistoryView } from "./components/HistoryView";
import { ImageSource } from "./components/ImageSource";
import { StatusAnnouncer } from "./components/StatusAnnouncer";
import { TranscriptionView } from "./components/TranscriptionView";
import { transcriptionSummary } from "./transcriptionText";
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

  const resultHeadingRef = useRef<HTMLHeadingElement | null>(null);

  const announce = useCallback((message: string, tone?: "info" | "error") => {
    if (tone === "error") {
      setError(message);
      setStatus("");
    } else {
      setStatus(message);
      setError("");
    }
  }, []);

  const clearMessages = () => {
    setStatus("");
    setError("");
  };

  // Título del documento dinámico: ayuda a orientarse con lector de pantalla.
  useEffect(() => {
    const base = "Chess Accessibility";
    document.title =
      view === "history" ? `Historial · ${base}` : `Analizar tablero · ${base}`;
  }, [view]);

  // Al completarse un análisis, lleva el foco al encabezado del resultado
  // para que el lector de pantalla empiece a leer ahí.
  useEffect(() => {
    if (analysis?.transcription && resultHeadingRef.current) {
      resultHeadingRef.current.focus();
    }
  }, [analysis]);

  const onImageSelected = useCallback((selected: File) => {
    setFile(selected);
  }, []);

  const onAnalyze = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      clearMessages();
      if (!file) {
        announce(
          "Primero elige una imagen: sube un archivo o haz una foto.",
          "error"
        );
        return;
      }
      setBusy(true);
      setStatus("Analizando la imagen del tablero. Espera un momento…");
      try {
        const result = await createAnalysis(file, mode);
        setAnalysis(result);
        if (result.status === "failed") {
          announce(result.error ?? "El análisis ha fallado.", "error");
        } else if (result.transcription) {
          setStatus(transcriptionSummary(result.transcription));
        } else {
          setStatus("Análisis completado.");
        }
        setHistoryKey((k) => k + 1);
      } catch (err) {
        announce(
          err instanceof Error
            ? `No se pudo conectar con el servidor: ${err.message}`
            : String(err),
          "error"
        );
      } finally {
        setBusy(false);
      }
    },
    [file, mode, announce]
  );

  const onConfirm = useCallback(async () => {
    if (!analysis) return;
    setBusy(true);
    clearMessages();
    try {
      await confirmResult(analysis.id);
      announce("Confirmación registrada. Gracias por tu revisión.");
    } catch (err) {
      announce(err instanceof Error ? err.message : String(err), "error");
    } finally {
      setBusy(false);
    }
  }, [analysis, announce]);

  const onSubmitCorrection = useCallback(
    async (corrected: BoardState) => {
      if (!analysis) return;
      setBusy(true);
      clearMessages();
      try {
        await submitCorrection(analysis.id, corrected);
        announce(
          "Corrección enviada. Pasará por revisión antes de usarse para mejorar el modelo."
        );
      } catch (err) {
        announce(err instanceof Error ? err.message : String(err), "error");
      } finally {
        setBusy(false);
      }
    },
    [analysis, announce]
  );

  const openFromHistory = useCallback(
    async (id: string) => {
      setBusy(true);
      clearMessages();
      try {
        const result = await getAnalysis(id);
        setAnalysis(result);
        setView("analyze");
        announce("Análisis cargado desde el historial.");
      } catch (err) {
        announce(err instanceof Error ? err.message : String(err), "error");
      } finally {
        setBusy(false);
      }
    },
    [announce]
  );

  return (
    <>
      <a href="#main" className="skip-link">
        Saltar al contenido principal
      </a>

      <header className="site-header">
        <div className="site-header__inner">
          <div className="brand">
            <span className="brand__mark" aria-hidden="true">
              ♞
            </span>
            <div>
              <h1>Chess Accessibility</h1>
              <p className="brand__tagline">
                De una imagen de un tablero a una transcripción braille accesible.
              </p>
            </div>
          </div>
          <nav className="tabs tabs--nav" aria-label="Secciones principales">
            <button
              type="button"
              role="tab"
              aria-selected={view === "analyze"}
              aria-current={view === "analyze" ? "page" : undefined}
              className={`tab ${view === "analyze" ? "tab--active" : ""}`}
              onClick={() => setView("analyze")}
            >
              Analizar
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={view === "history"}
              aria-current={view === "history" ? "page" : undefined}
              className={`tab ${view === "history" ? "tab--active" : ""}`}
              onClick={() => setView("history")}
            >
              Historial
            </button>
          </nav>
        </div>
      </header>

      <main id="main" className="container" aria-busy={busy}>
        <StatusAnnouncer
          message={error || status}
          tone={error ? "error" : "info"}
          busy={busy}
        />

        {view === "analyze" && (
          <>
            <section className="card" aria-labelledby="upload-heading">
              <h2 id="upload-heading" className="card__title">
                <span className="step-number" aria-hidden="true">
                  1
                </span>
                Elige el modo y aporta la imagen
              </h2>

              <form onSubmit={onAnalyze} className="analyze-form">
                <fieldset className="mode-fieldset">
                  <legend>Modo de uso</legend>
                  <div className="mode-options">
                    <label className={`mode-card ${mode === "blind" ? "mode-card--active" : ""}`}>
                      <input
                        type="radio"
                        name="mode"
                        value="blind"
                        checked={mode === "blind"}
                        onChange={() => setMode("blind")}
                      />
                      <span className="mode-card__title">
                        <span aria-hidden="true">🔊</span> Persona ciega
                      </span>
                      <span className="mode-card__desc">
                        Lectura directa de la transcripción, sin edición.
                      </span>
                    </label>
                    <label className={`mode-card ${mode === "sighted" ? "mode-card--active" : ""}`}>
                      <input
                        type="radio"
                        name="mode"
                        value="sighted"
                        checked={mode === "sighted"}
                        onChange={() => setMode("sighted")}
                      />
                      <span className="mode-card__title">
                        <span aria-hidden="true">✏️</span> Persona vidente
                      </span>
                      <span className="mode-card__desc">
                        Permite revisar y corregir antes de guardar.
                      </span>
                    </label>
                  </div>
                </fieldset>

                <ImageSource
                  onImageSelected={onImageSelected}
                  onAnnounce={announce}
                  disabled={busy}
                />

                <div className="analyze-form__actions">
                  <button
                    type="submit"
                    className="btn btn--primary btn--lg"
                    disabled={busy || !file}
                  >
                    {busy ? (
                      <>
                        <span className="spinner" aria-hidden="true" /> Procesando…
                      </>
                    ) : (
                      "Analizar tablero"
                    )}
                  </button>
                  {!file && (
                    <span className="hint" role="note">
                      Elige una imagen para activar el análisis.
                    </span>
                  )}
                </div>
              </form>
            </section>

            {analysis?.transcription && (
              <section className="card" aria-labelledby="result-heading">
                <h2
                  id="result-heading"
                  className="card__title"
                  tabIndex={-1}
                  ref={resultHeadingRef}
                >
                  <span className="step-number" aria-hidden="true">
                    2
                  </span>
                  Transcripción
                </h2>
                <TranscriptionView
                  transcription={analysis.transcription}
                  onAnnounce={announce}
                />

                {mode === "sighted" && analysis.board_state && (
                  <div className="subsection">
                    <h3 className="subsection__title">
                      <span className="step-number" aria-hidden="true">
                        3
                      </span>
                      Revisión y corrección
                    </h3>
                    <CorrectionEditor
                      board={analysis.board_state}
                      onConfirm={onConfirm}
                      onSubmitCorrection={onSubmitCorrection}
                      busy={busy}
                    />
                  </div>
                )}
              </section>
            )}

            {analysis?.status === "failed" && (
              <section
                className="card callout callout--error"
                aria-labelledby="failed-heading"
              >
                <h2 id="failed-heading" className="card__title">
                  <span aria-hidden="true">⚠️</span> No se pudo analizar la imagen
                </h2>
                <p>{analysis.error}</p>
                <p className="hint">
                  Prueba con una foto más nítida, bien iluminada y con el tablero
                  encuadrado de frente.
                </p>
              </section>
            )}
          </>
        )}

        {view === "history" && (
          <section className="card" aria-labelledby="history-heading">
            <h2 id="history-heading" className="card__title">
              Historial de análisis
            </h2>
            <HistoryView onOpen={openFromHistory} refreshKey={historyKey} />
          </section>
        )}
      </main>

      <footer className="site-footer">
        <p>
          Transcripción basada en la signografía braille de la Comisión Braille
          Española (Reto Ajedrez ONCE).
        </p>
      </footer>
    </>
  );
}
