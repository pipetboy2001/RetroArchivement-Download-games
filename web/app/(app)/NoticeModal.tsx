"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "ra-downloader-notice-seen";

export default function NoticeModal() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!sessionStorage.getItem(STORAGE_KEY)) setOpen(true);
  }, []);

  function dismiss() {
    sessionStorage.setItem(STORAGE_KEY, "1");
    setOpen(false);
  }

  if (!open) return null;

  return (
    <div
      className="modal-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) dismiss();
      }}
    >
      <div className="modal-panel">
        <div className="modal-head">
          <h2>Antes de descargar</h2>
          <button type="button" className="modal-close" onClick={dismiss} aria-label="Cerrar">
            &times;
          </button>
        </div>
        <div className="modal-body">
          <p style={{ margin: 0 }}>
            Nota: Para descargar, primero inicia sesión en{" "}
            <a href="https://archive.org/" target="_blank" rel="noopener" style={{ color: "var(--link)" }}>
              archive.org
            </a>
            . Los juegos no son de mi propiedad; todo el contenido está alojado en archive.org. Esta
            herramienta solo facilita enlaces de ROMs compatibles con RetroAchievements. Consulta la{" "}
            <a href="/faq" style={{ color: "var(--link)" }}>
              FAQ y Aviso legal
            </a>
            .
          </p>
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end", padding: "0 18px 16px" }}>
          <button type="button" className="btn-primary" onClick={dismiss}>
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
}
