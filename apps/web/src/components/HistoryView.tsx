// Historial de análisis. Permite reabrir un análisis para revisarlo/confirmarlo.
import { useEffect, useState } from "react";
import { getHistory } from "../api";
import type { HistoryItem } from "../types";

interface Props {
  onOpen: (id: string) => void;
  refreshKey: number;
}

const STATUS_LABELS: Record<string, string> = {
  completed: "Completado",
  processing: "Procesando",
  created: "Creado",
  failed: "Fallido",
};

export function HistoryView({ onOpen, refreshKey }: Props) {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getHistory()
      .then((data) => active && setItems(data))
      .catch((e) => active && setError(String(e.message ?? e)));
    return () => {
      active = false;
    };
  }, [refreshKey]);

  if (error) {
    return <p role="alert">No se pudo cargar el historial: {error}</p>;
  }
  if (items.length === 0) {
    return <p>Todavía no hay análisis en el historial.</p>;
  }

  return (
    <table>
      <caption className="visually-hidden">Historial de análisis</caption>
      <thead>
        <tr>
          <th scope="col">Fecha</th>
          <th scope="col">Modo</th>
          <th scope="col">Estado</th>
          <th scope="col">Acción</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{new Date(item.created_at).toLocaleString("es-ES")}</td>
            <td>{item.mode === "blind" ? "Ciego" : "Vidente"}</td>
            <td>{STATUS_LABELS[item.status] ?? item.status}</td>
            <td>
              <button
                type="button"
                onClick={() => onOpen(item.id)}
                aria-label={`Abrir análisis del ${new Date(
                  item.created_at
                ).toLocaleString("es-ES")}`}
              >
                Abrir
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
