// Región ARIA-live que anuncia cambios de estado a los lectores de pantalla.
// El mensaje también se muestra visualmente (no depende solo del canal auditivo).

interface Props {
  message: string;
  tone?: "info" | "error";
  busy?: boolean;
}

export function StatusAnnouncer({ message, tone = "info", busy = false }: Props) {
  if (!message) {
    // Mantener el nodo live en el DOM para que los cambios se anuncien.
    return (
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="visually-hidden"
      />
    );
  }
  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      aria-live={tone === "error" ? "assertive" : "polite"}
      aria-atomic="true"
      className={`status status--${tone}`}
    >
      {busy && tone !== "error" ? (
        <span className="spinner spinner--inline" aria-hidden="true" />
      ) : (
        <span aria-hidden="true" className="status__icon">
          {tone === "error" ? "⚠️" : "ℹ️"}
        </span>
      )}
      {/* Prefijo textual para no depender solo del color/icono. */}
      <span>
        <strong>{tone === "error" ? "Error: " : "Estado: "}</strong>
        {message}
      </span>
    </div>
  );
}
