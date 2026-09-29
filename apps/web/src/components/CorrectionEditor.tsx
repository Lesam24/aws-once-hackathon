// Editor de corrección para modo vidente. Permite revisar y corregir las piezas
// detectadas antes de enviar el feedback. Totalmente navegable por teclado.
import { useState } from "react";
import type { BoardState, Color, Piece, PieceType } from "../types";

const PIECE_TYPES: PieceType[] = [
  "king",
  "queen",
  "rook",
  "bishop",
  "knight",
  "pawn",
];
const PIECE_LABELS: Record<PieceType, string> = {
  king: "Rey",
  queen: "Dama",
  rook: "Torre",
  bishop: "Alfil",
  knight: "Caballo",
  pawn: "Peón",
};
const COLOR_LABELS: Record<Color, string> = { white: "Blanca", black: "Negra" };

interface Props {
  board: BoardState;
  onConfirm: () => void;
  onSubmitCorrection: (corrected: BoardState) => void;
  busy: boolean;
}

export function CorrectionEditor({
  board,
  onConfirm,
  onSubmitCorrection,
  busy,
}: Props) {
  const [pieces, setPieces] = useState<Piece[]>(board.pieces);

  function updatePiece(index: number, patch: Partial<Piece>) {
    setPieces((prev) =>
      prev.map((p, i) => (i === index ? { ...p, ...patch } : p))
    );
  }

  function removePiece(index: number) {
    setPieces((prev) => prev.filter((_, i) => i !== index));
  }

  function addPiece() {
    setPieces((prev) => [
      ...prev,
      { color: "white", type: "pawn", square: "a2", confidence: 1 },
    ]);
  }

  function submit() {
    onSubmitCorrection({ ...board, pieces });
  }

  return (
    <div className="editor">
      <p id="editor-help">
        Revisa las piezas detectadas. Puedes editar el color, el tipo y la casilla,
        eliminar piezas o añadir las que falten. Si todo es correcto, confírmalo.
      </p>
      <table aria-describedby="editor-help">
        <caption className="visually-hidden">
          Piezas detectadas, editables por fila
        </caption>
        <thead>
          <tr>
            <th scope="col">Color</th>
            <th scope="col">Pieza</th>
            <th scope="col">Casilla</th>
            <th scope="col">Acción</th>
          </tr>
        </thead>
        <tbody>
          {pieces.map((piece, i) => (
            <tr key={i}>
              <td>
                <label className="visually-hidden" htmlFor={`color-${i}`}>
                  Color de la pieza {i + 1}
                </label>
                <select
                  id={`color-${i}`}
                  value={piece.color}
                  onChange={(e) =>
                    updatePiece(i, { color: e.target.value as Color })
                  }
                >
                  {(["white", "black"] as Color[]).map((c) => (
                    <option key={c} value={c}>
                      {COLOR_LABELS[c]}
                    </option>
                  ))}
                </select>
              </td>
              <td>
                <label className="visually-hidden" htmlFor={`type-${i}`}>
                  Tipo de la pieza {i + 1}
                </label>
                <select
                  id={`type-${i}`}
                  value={piece.type}
                  onChange={(e) =>
                    updatePiece(i, { type: e.target.value as PieceType })
                  }
                >
                  {PIECE_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {PIECE_LABELS[t]}
                    </option>
                  ))}
                </select>
              </td>
              <td>
                <label className="visually-hidden" htmlFor={`square-${i}`}>
                  Casilla de la pieza {i + 1}
                </label>
                <input
                  id={`square-${i}`}
                  type="text"
                  inputMode="text"
                  maxLength={2}
                  pattern="[a-h][1-8]"
                  value={piece.square}
                  onChange={(e) =>
                    updatePiece(i, { square: e.target.value.toLowerCase() })
                  }
                />
              </td>
              <td>
                <button
                  type="button"
                  onClick={() => removePiece(i)}
                  aria-label={`Eliminar pieza ${i + 1} en ${piece.square}`}
                >
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="editor-actions">
        <button type="button" onClick={addPiece}>
          Añadir pieza
        </button>
        <button type="button" onClick={submit} disabled={busy}>
          Enviar corrección
        </button>
        <button type="button" onClick={onConfirm} disabled={busy}>
          Confirmar que es correcto
        </button>
      </div>
    </div>
  );
}
