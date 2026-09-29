// Tipos del frontend que reflejan los contratos v1 del backend (chess_contracts).
// Mantener alineados con packages/contracts/src/chess_contracts/models.py.

export type Color = "white" | "black";
export type PieceType =
  | "king"
  | "queen"
  | "bishop"
  | "knight"
  | "rook"
  | "pawn";

export type BoardOrientation =
  | "white-at-bottom"
  | "black-at-bottom"
  | "unknown";

export type AnalysisStatus = "created" | "processing" | "completed" | "failed";
export type AccessMode = "blind" | "sighted";

export interface Piece {
  color: Color;
  type: PieceType;
  square: string;
  confidence: number;
}

export interface BoardState {
  contract_version?: string;
  orientation: BoardOrientation;
  pieces: Piece[];
  highlights?: unknown[];
  arrows?: unknown[];
  model_version?: string | null;
  pipeline_version?: string | null;
}

export interface TranscriptionLine {
  text: string;
  square?: string | null;
  readable?: string | null;
}

export interface Transcription {
  format_version: string;
  white_lines: TranscriptionLine[];
  black_lines: TranscriptionLine[];
  highlights: string[];
  arrows: string[];
  warnings: string[];
}

export interface ValidationIssue {
  code: string;
  message: string;
  severity: "info" | "warning" | "error";
  square?: string | null;
}

export interface ValidationResult {
  ok: boolean;
  issues: ValidationIssue[];
}

export interface Analysis {
  id: string;
  status: AnalysisStatus;
  mode: AccessMode;
  created_at: string;
  updated_at: string;
  board_state?: BoardState | null;
  validation?: ValidationResult | null;
  transcription?: Transcription | null;
  model_version?: string | null;
  pipeline_version?: string | null;
  error?: string | null;
}

export interface HistoryItem {
  id: string;
  status: string;
  mode: string;
  created_at: string;
}
