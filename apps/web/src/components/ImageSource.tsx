// Fuente de imagen del tablero con dos vías accesibles:
//  1) Subir un archivo (input file).
//  2) Hacer una foto con la cámara (getUserMedia); si no está disponible,
//     recae en la captura nativa del móvil (input capture="environment").
//
// Todo es navegable por teclado y anuncia su estado a los lectores de pantalla.
import { useCallback, useEffect, useRef, useState } from "react";

interface Props {
  onImageSelected: (file: File, previewUrl: string) => void;
  onAnnounce: (message: string, tone?: "info" | "error") => void;
  disabled?: boolean;
}

type Tab = "upload" | "camera";

export function ImageSource({ onImageSelected, onAnnounce, disabled }: Props) {
  const [tab, setTab] = useState<Tab>("upload");
  const [cameraActive, setCameraActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [cameraSupported] = useState(
    () =>
      typeof navigator !== "undefined" &&
      !!navigator.mediaDevices &&
      typeof navigator.mediaDevices.getUserMedia === "function"
  );

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const nativeCaptureRef = useRef<HTMLInputElement | null>(null);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  }, []);

  // Libera la cámara y las URLs de objeto al desmontar.
  useEffect(() => {
    return () => {
      stopCamera();
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const usePreview = useCallback(
    (file: File) => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setFileName(file.name);
      onImageSelected(file, url);
    },
    [onImageSelected, previewUrl]
  );

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    usePreview(file);
    onAnnounce(`Imagen seleccionada: ${file.name}. Lista para analizar.`);
  };

  const startCamera = useCallback(async () => {
    if (!cameraSupported) {
      // Fallback: abre la cámara nativa del dispositivo.
      nativeCaptureRef.current?.click();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play().catch(() => undefined);
      }
      setCameraActive(true);
      onAnnounce(
        "Cámara activada. Encuadra el tablero y pulsa Capturar foto."
      );
    } catch (err) {
      const name = err instanceof DOMException ? err.name : "";
      const msg =
        name === "NotAllowedError"
          ? "Permiso de cámara denegado. Puedes subir un archivo en su lugar."
          : name === "NotFoundError"
            ? "No se ha encontrado ninguna cámara. Sube un archivo en su lugar."
            : "No se pudo acceder a la cámara. Sube un archivo en su lugar.";
      onAnnounce(msg, "error");
      setTab("upload");
    }
  }, [cameraSupported, onAnnounce]);

  const capturePhoto = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
      if (!blob) {
        onAnnounce("No se pudo capturar la foto. Inténtalo de nuevo.", "error");
        return;
      }
      const file = new File([blob], `captura-${Date.now()}.png`, {
        type: "image/png",
      });
      usePreview(file);
      stopCamera();
      onAnnounce("Foto capturada. Lista para analizar.");
    }, "image/png");
  }, [onAnnounce, stopCamera, usePreview]);

  const switchTab = (next: Tab) => {
    if (next === tab) return;
    if (next === "upload") stopCamera();
    setTab(next);
  };

  return (
    <div className="image-source">
      <div
        className="tabs"
        role="tablist"
        aria-label="Cómo aportar la imagen del tablero"
      >
        <button
          type="button"
          role="tab"
          id="tab-upload"
          aria-selected={tab === "upload"}
          aria-controls="panel-upload"
          tabIndex={tab === "upload" ? 0 : -1}
          className={`tab ${tab === "upload" ? "tab--active" : ""}`}
          onClick={() => switchTab("upload")}
        >
          <span aria-hidden="true">📁</span> Subir archivo
        </button>
        <button
          type="button"
          role="tab"
          id="tab-camera"
          aria-selected={tab === "camera"}
          aria-controls="panel-camera"
          tabIndex={tab === "camera" ? 0 : -1}
          className={`tab ${tab === "camera" ? "tab--active" : ""}`}
          onClick={() => switchTab("camera")}
        >
          <span aria-hidden="true">📷</span> Hacer una foto
        </button>
      </div>

      {tab === "upload" && (
        <div
          role="tabpanel"
          id="panel-upload"
          aria-labelledby="tab-upload"
          className="tabpanel"
        >
          <label htmlFor="image" className="field-label">
            Imagen del tablero
          </label>
          <input
            id="image"
            type="file"
            accept="image/*"
            onChange={onFileChange}
            disabled={disabled}
          />
          <p className="hint">
            Formatos de imagen (PNG, JPG…). También puedes arrastrar el archivo aquí.
          </p>
        </div>
      )}

      {tab === "camera" && (
        <div
          role="tabpanel"
          id="panel-camera"
          aria-labelledby="tab-camera"
          className="tabpanel"
        >
          {!cameraActive ? (
            <>
              <p className="hint">
                Se pedirá permiso para usar la cámara. La imagen no sale de tu
                dispositivo hasta que pulses Analizar.
              </p>
              <button
                type="button"
                className="btn btn--primary"
                onClick={startCamera}
                disabled={disabled}
              >
                <span aria-hidden="true">📷</span> Activar cámara
              </button>
            </>
          ) : (
            <div className="camera-live">
              <video
                ref={videoRef}
                className="camera-video"
                playsInline
                muted
                aria-label="Vista previa de la cámara en directo"
              />
              <div className="camera-actions">
                <button
                  type="button"
                  className="btn btn--primary"
                  onClick={capturePhoto}
                >
                  <span aria-hidden="true">📸</span> Capturar foto
                </button>
                <button type="button" className="btn" onClick={stopCamera}>
                  Cancelar
                </button>
              </div>
            </div>
          )}

          {/* Fallback de captura nativa (móviles sin getUserMedia). */}
          <input
            ref={nativeCaptureRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="visually-hidden"
            onChange={onFileChange}
            tabIndex={-1}
            aria-hidden="true"
          />
        </div>
      )}

      {previewUrl && (
        <figure className="preview">
          <img
            src={previewUrl}
            alt={
              fileName
                ? `Vista previa de la imagen seleccionada: ${fileName}`
                : "Vista previa de la imagen del tablero seleccionada"
            }
            className="preview-img"
          />
          <figcaption className="hint">
            {fileName ?? "Imagen lista"} — pulsa Analizar tablero para continuar.
          </figcaption>
        </figure>
      )}
    </div>
  );
}
