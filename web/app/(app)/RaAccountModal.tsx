"use client";

import { UserIcon } from "./icons";

export default function RaAccountModal({ open, onClose }: { open: boolean; onClose: () => void }) {
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
          <h2>Conectar RetroAchievements</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Cerrar">
            &times;
          </button>
        </div>
        <div className="modal-body">
          <div className="soon-panel">
            <UserIcon size={32} />
            <h3>Próximamente</h3>
            <p>
              Vas a poder conectar tu cuenta con tu propia Web API Key (nunca se guarda en nuestro servidor)
              para traer tu lista &quot;Want to Play&quot; y ver qué juegos ya tenemos disponibles para descargar.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
