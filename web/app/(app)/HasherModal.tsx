"use client";

import { FingerprintIcon } from "./icons";

export default function HasherModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null;

  return (
    <div
      className="modal-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="modal-panel" style={{ maxWidth: 420 }}>
        <div className="modal-head">
          <h2>Verificar ROM</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Cerrar">
            &times;
          </button>
        </div>
        <div className="modal-body">
          <div className="soon-panel">
            <FingerprintIcon size={32} />
            <h3>Próximamente</h3>
            <p>
              Vas a poder arrastrar tu ROM acá para calcular su hash MD5 en el navegador (sin subir el archivo
              a ningún lado) y verificar si coincide con la versión que pide RetroAchievements.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
