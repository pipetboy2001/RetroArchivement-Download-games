"use client";

import { useRef, useState } from "react";
import { useCart } from "./CartContext";
import { downloadGame } from "./download";
import { BoltIcon, CheckCircleIcon, CheckIcon, ShieldCheckIcon, TrashIcon, UploadIcon, WarningIcon } from "./icons";
import { computeRaHash } from "./raHash";
import { lookupHash } from "./verifyHash";
import type { SearchResult } from "./types";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB"];
  let value = bytes;
  let unitIndex = -1;
  do {
    value /= 1024;
    unitIndex++;
  } while (value >= 1024 && unitIndex < units.length - 1);
  return `${value.toFixed(1)} ${units[unitIndex]}`;
}

export default function HasherModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const cart = useCart();
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hash, setHash] = useState("");
  const [consoleGuess, setConsoleGuess] = useState("");
  const [fileInfo, setFileInfo] = useState<{ name: string; size: number } | null>(null);
  const [result, setResult] = useState<SearchResult | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  if (!open) return null;

  function reset() {
    setError("");
    setHash("");
    setConsoleGuess("");
    setFileInfo(null);
    setResult(null);
  }

  async function handleFile(file: File) {
    reset();
    setFileInfo({ name: file.name, size: file.size });
    const buffer = new Uint8Array(await file.arrayBuffer());
    const computed = computeRaHash(file.name, buffer);
    if ("error" in computed) {
      setError(computed.error);
      return;
    }
    setHash(computed.hash);
    setConsoleGuess(computed.consoleGuess);

    setLoading(true);
    try {
      const data = await lookupHash(computed.hash);
      if (data.success) setResult(data);
      else setError(data.message || "No se encontró ese hash en la base de datos.");
    } catch {
      setError("No se pudo verificar el hash.");
    } finally {
      setLoading(false);
    }
  }

  function addToCart() {
    if (!result) return;
    cart.add({
      id: hash,
      name: result.name ?? hash,
      consoles: result.console ? [result.console] : [],
      image_icon: null,
      achievements: null,
      hash,
      rom_path: "",
    });
  }

  const fullyVerified = !!result?.ra_recognized && !!result?.link_ok;

  return (
    <div
      className="modal-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          reset();
          onClose();
        }
      }}
    >
      <div className="modal-panel">
        <div className="modal-head">
          <h2>
            Verificar ROM <CheckCircleIcon className="title-badge" />
          </h2>
          <button
            type="button"
            className="modal-close"
            onClick={() => {
              reset();
              onClose();
            }}
            aria-label="Cerrar"
          >
            &times;
          </button>
        </div>
        <div className="modal-body">
          {!result && (
            <div
              className={`hasher-dropzone${dragOver ? " drag-over" : ""}`}
              onClick={() => inputRef.current?.click()}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                const file = e.dataTransfer.files[0];
                if (file) void handleFile(file);
              }}
            >
              <UploadIcon className="upload-icon" />
              <h3>Soltá tu ROM acá</h3>
              <p className="hasher-dropzone-sub">o hacé clic para explorar tu equipo</p>
              <button
                type="button"
                className="btn-ghost hasher-select-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  inputRef.current?.click();
                }}
              >
                <UploadIcon size={14} />
                <span>Seleccionar archivo</span>
              </button>
              <div className="hasher-badges">
                {[".zip", "NES", "SNES", "GBA", "N64", "Genesis"].map((label) => (
                  <span key={label} className="hasher-badge">
                    {label}
                  </span>
                ))}
              </div>
              <input
                ref={inputRef}
                type="file"
                style={{ display: "none" }}
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) void handleFile(file);
                  e.target.value = "";
                }}
              />
            </div>
          )}

          <div className="hasher-note">
            <ShieldCheckIcon />
            <span>
              Se calcula el hash MD5 en tu navegador, nunca se sube a ningún lado. Soporta .zip y las
              consolas de cartucho más comunes (CD/disco todavía no).
            </span>
          </div>
          <p className="hasher-disc-note">
            ¿Necesitás verificar discos (PS1, PS2, Saturn...)? Probá{" "}
            <a
              href="https://github.com/Siallus/RetroAchievementsLibraryValidator"
              target="_blank"
              rel="noopener"
              style={{ color: "var(--link)" }}
            >
              RetroAchievementsLibraryValidator
            </a>
            , corre en tu PC con el RAHasher oficial.
          </p>

          {loading && <p className="empty-hint">Verificando hash…</p>}
          {error && <p className="empty-hint">{error}</p>}

          {result && (
            <div className={`hasher-result ${fullyVerified ? "ok" : "warn"}`}>
              <div className="hasher-result-title">
                {fullyVerified ? <CheckCircleIcon /> : <WarningIcon />}
                {fullyVerified ? "Archivo reconocido" : "Archivo encontrado"}
              </div>

              <div className="hasher-result-grid">
                <div>
                  <h4>Archivo local</h4>
                  <dl>
                    <div>
                      <dt>Nombre:</dt> <dd>{fileInfo?.name ?? "—"}</dd>
                    </div>
                    <div>
                      <dt>Tamaño:</dt> <dd>{fileInfo ? formatBytes(fileInfo.size) : "—"}</dd>
                    </div>
                    <div>
                      <dt>Hash MD5:</dt> <dd className="mono">{hash}</dd>
                    </div>
                  </dl>
                </div>
                <div>
                  <h4>RetroAchievements</h4>
                  <dl>
                    <div>
                      <dt>Juego:</dt> <dd>{result.name ?? "—"}</dd>
                    </div>
                    <div>
                      <dt>Plataforma:</dt> <dd>{result.console ?? consoleGuess}</dd>
                    </div>
                    <div>
                      <dt>Reconocido:</dt> <dd>{result.ra_recognized ? "Sí" : "No"}</dd>
                    </div>
                    <div>
                      <dt>Enlace:</dt> <dd>{result.link_ok ? "Verificado" : "No verificado"}</dd>
                    </div>
                  </dl>
                </div>
              </div>

              <div className="hasher-result-actions">
                <button type="button" className="btn-ghost" onClick={() => downloadGame(hash, result.name)}>
                  <BoltIcon /> Descargar
                </button>
                <button type="button" className="btn-ghost" disabled={cart.has(hash)} onClick={addToCart}>
                  {cart.has(hash) ? (
                    <span key="added" className="icon-pop" style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                      <CheckIcon /> En el carrito
                    </span>
                  ) : (
                    "Agregar al carrito"
                  )}
                </button>
                <button type="button" className="btn-ghost hasher-remove-btn" onClick={reset}>
                  <TrashIcon /> Quitar archivo
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
