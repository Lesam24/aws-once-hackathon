// Región ARIA-live que anuncia cambios de estado a los lectores de pantalla.
// El mensaje también se muestra visualmente (no depende solo del canal auditivo).

interface Props {
  message: string;
  tone?: "info" | "error";
}

export function StatusAnnouncer({ message, tone = "info" }: Props) {
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
      {/* Prefijo textual para no depender solo del color. */}
      <strong>{tone === "error" ? "Error: " : "Estado: "}</strong>
      {message}
    </div>
  );
}
